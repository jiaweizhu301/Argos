import src.database as db
import numpy as np
from sklearn.svm import SVR
from sklearn import linear_model
import math
import copy
import scipy.stats as stats
from datetime import datetime
from random import randint

# Process stock info and calc level
def processData(data):  

    #define number of timeline data
    historicalPricesSize = len(data.prices)
    X = []

    #add in simple x values as time
    for time_value in range(historicalPricesSize):
        X.append([time_value])

    #define number of values of a stock's data
    y = []
    
    #original prices
    copied_data_prices = copy.deepcopy(data.prices)
    original_prices = []
    for y_counter in range(historicalPricesSize-1,0,-1):
        if y_counter == 0:
            original_prices.append(0)
        elif y_counter == range(historicalPricesSize):
            original_prices.append(0)
        else:
            original_prices.append((float(copied_data_prices[y_counter].price)))
   
    #insert 'returns of investments'
    for y_counter in range(historicalPricesSize):
        #return = ((currentPrice / secondLastPrice) - 1) * 100%
        if y_counter == 0:
            insertingReturn = 0
        elif y_counter == range(historicalPricesSize):
            insertingReturn = 0
        else:
            insertingReturn = (float(data.prices[y_counter].price) / float(data.prices[y_counter - 1].price) - 1) * 100
        y.append(insertingReturn)

    # Fit regression model
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
    fittedModel  =  svr_rbf.fit(X, y)

    #make prediction using giving training data (in this case the prediction will be simply drawing the original historical graph)
    y_rbf = fittedModel.predict(X)

    #do ACTUAL prediction by giving NEW specific times, as new x_values in x_predicting
    newTimeSize = 2     #that is, we are predicting the next 2 updates

    X_predicting = []
    for i in range(newTimeSize):
        X_predicting.append([i+historicalPricesSize])

    #predict using the new x_values given in "X_predicting"
    y_predicting = fittedModel.predict(X_predicting)

    #provide overview of everything (both historical and future values) all in one graph
    X_all = X
    y_all = y
    for newTime_value in range(newTimeSize):
        X_all.append(X_predicting[newTime_value])
    for newPrediction_result in y_predicting:
        y_all.append(newPrediction_result)

    # Calc var and trend
    trend = findTrend(X_all , y_all)[0]
    variance = findVariance(data.ticker)

    #find confidence value (that is, how much we believe the AI prediction will be accurate)
    if len(y_all) > 0:
        confidence = findConfidenceValue(y_all)
    else:
        confidence = 0.99

    #use primary function specified by our client, to find the action for treating a stock
    if len(y) > 0 :
        action = findActionPrimary(X , y)
    
    #use secondary function to find the action for treating a stock (if the stock was said to be undetermined from primary computation)
    if action == 'U':
        action = findActionSecondary(trend, variance, confidence)

    #perform last classification if above 2 functions do not provide further information about recommendation
    if action == 'U':
        action = findActionFinal(trend)

    # Get description and store all in db
    summary = getSummary(variance, trend, confidence, action)
    last = data.prices[0]
    db.store_stock_info(data.ticker, variance, trend, last.price, datetime.today(),confidence, action, summary)

#function to return action of buying or selling
def findActionPrimary(original_Xs, original_ys):

    #set default_action to be undetermined
    default_action = 'U'

    #initialise maximum value of a stock
    maxValue = 0

    #if the stock is at peak value over this amount of updates, then we suggest selling the stock
    num_updates = 15  

    #check only past 'num_update' updates of a stock's values
    if len(original_ys) > num_updates:
        #find maximum value
        for updateCount in range(num_updates):
            if original_ys[updateCount] > maxValue:
                maxValue = original_ys[updateCount]

    #if there is less than 'num_update' updates info available, check all available historical prices
    else:
        #find maximum value 
        for updateCount in range(len(original_ys)):
            if original_ys[updateCount] > maxValue:
                maxValue = original_ys[updateCount]
    
    #return action of selling, if the current value is largest out of last 'num_update' updates
    if original_ys[len(original_ys) - 1] >= maxValue:
        return 'S'
    

    #############The below is for buying: if it is reducing values in a decreased rate, then we suggest buying the stock#########
    #the number of updates we check, for the decreasing trends of a stock 
    num_gradient_calc = 3

    #the interval between 2 stock values that we used for calculation of a gradient
    gradient_interval = 1

    #find gradients of the past 'gradient_calc_interval' updates
    naiveGradients = []

    #append all gradients of the lastest 'num_gradient_calc' updates, each calculated from two stock values 'gradient_interval' further apart
    if len(original_ys) > num_gradient_calc:
        for gradientCount in range(num_gradient_calc):
            #gradient = (y2-y1)/(x2-x1)
            naiveGradients.append(( original_ys[len(original_ys) - gradientCount - 1]
                                 - original_ys[len(original_ys) - gradientCount - gradient_interval] )
                                / 1)
    
    #if we find the rate of decreasing is reduced, we should suggest buying the potential raising stock in the near future
    decreasing_rate = True
    for gradientCount in range(len(naiveGradients) - 1):
        if (naiveGradients[gradientCount] < naiveGradients[gradientCount + 1]):
                decreasing_rate = False

    #we are also selling the stocks that do not change over the measured period of time (its values are being extremely constant)
    if decreasing_rate == True:
        return 'B'

    return default_action


#secondary function to return action of buying or selling, if primary function did not specify a clear answer
def findActionSecondary(trend, variance, confidence):

    #set default_action to be undetermined
    default_action = 'U'

    #if the stock is increasing in values but having higher risk of changing, then we suggest selling the volatile stock
    if ((trend > 0) and (variance >= 0.04) and (confidence > 0.5)):
        return 'S'
      
    #if the stock is increasing in values and also having lower risk of changing, then we suggest buying the stable stock
    elif ((trend > 0) and (variance < 0.04) and (confidence > 0.5)):
        return 'B'
        
    #if the stock is decreasing in values but having higher risk of changing, then we suggest buying the potentially benificial stock
    elif ((trend < 0) and (variance >= 0.04) and (confidence > 0.5)):
        return 'B'
        
    #if the stock is decreasing in values and also having lower risk of changing, then we suggest selling the stock with poor-performance
    elif ((trend < 0) and (variance < 0.04) and (confidence > 0.5)):
        return 'S'

    return default_action

#final function to determine suggesting selling/buying a stock if the above 2 functions cannot do further classifications
def findActionFinal(trend):

    #simply suggest buying if it is a going well
    if trend > 0:
        return 'B'

    #simply suggest selling if it is performing badly
    else:
        return 'S'
    
#function to return confidence value, applying statistical concept of confidence interval
def findConfidenceValue(y_all):

    #exclude the stock having limited historical data (because we have 2 predicted values, we check 3 data points)
    if len(y_all) < 3:
        return 1

    #deep copy of y values provided (stock prices)
    y = copy.deepcopy(y_all)

    #extract sample
    sample_size = len(y)
    sample = y

    #the probability of a chosen stock's value is within the range of the later-derived confidence interval
    lower_tail_probability = 0.9

    #initialise z_critical value
    z_critical = stats.norm.ppf(q = lower_tail_probability)  

    #Below is for confidence interval calculation 
    #Get the population standard deviation
    pop_stdev = np.std(sample)  

    margin_of_error = z_critical * (pop_stdev/math.sqrt(sample_size))

    confidence_interval = (np.mean(sample) - margin_of_error,
                        np.mean(sample) + margin_of_error)  

    #minimum, maximum and mean value for confidence interval
    confidence_interval_min = confidence_interval[0]
    confidence_interval_max = confidence_interval[1]
    confidence_interval_mid = (confidence_interval_min + confidence_interval_max) / 2

    #distance from the predicted value to the middle of the confidence interval
    distance_to_mid = np.absolute(y[len(y)-1] - confidence_interval_mid)

    #distance from maximum or minimum to the middle of the confidence interval
    distance_interval = np.absolute(confidence_interval_max - confidence_interval_mid)
    
    #cannot divide by 0 (and avoid the warning "invalid value encountered in couble_scalars")
    if distance_interval * 10000000 < 1:
        return 0.95

    #distance ratio for converting relative distance to middle of the confidence interval
    distance_ratio = distance_to_mid / distance_interval

    #probability of a value 'not within the range of confidence interval of the actual stock population'
    reverse_low_tail_probability = 1 - lower_tail_probability

    #set the convidence value to be "how far away our predicted value is, from the middle of the confidence interval calculated using historical prices"
    convidence_value = np.absolute(1 - (distance_ratio * reverse_low_tail_probability))

    #set the default confidence value if the statistical method did not find it (due to lacking of historical data)
    if convidence_value == None:
        return 0.95

    # absolute value of the confidence value
    if convidence_value <= 0 or convidence_value > 1:
        return 0.95

    return convidence_value
    
#find the trend for a specific stock, by giving the change in values between "averaged predicted values" and "averaged original values" of the stock
def findTrend(X_all, y_all):

    #deepcopy everything
    X = copy.deepcopy(X_all)
    y = copy.deepcopy(y_all)

    # Create linear regression object
    regression = linear_model.LinearRegression()

    # Train the model using the training sets
    regression.fit(X, y)

    #X values we use to predict using linear regression (using the last and the next return-values to find gradient)
    X_predicting = np.array([len(X_all) - 12 , len(X_all) - 1]).reshape(-1,1) #using both the last and the 11st last x_values to predict, which means we get the trend for last 60 minutes
    
    # Make predictions using the X values above
    y_predicted = regression.predict(X_predicting)

    #gradient = (y2-y1)/(x2-x1)
    gradient = (y_predicted[1] - y_predicted[0]) / (X_predicting[1] - X_predicting[0])

    return gradient

#calculate the variance, representing risk
#find the variance which in proportion to the amount of historcial data
def findVariance(stock):

    original_prices = db.get_price_history(stock)['prices']
    old_Ys = db.get_price_history(stock)['prices']

    #specify the interval for checking variance
    num_updates_for_variance = 15

    #temp array storing 'returns of investments' for variance calculation
    new_array_returns = []

    #temp array storing 'prices' for variance calculation
    new_array_prices = []

    #max in prices, ignoring none values
    maxPrice = 0
    for i in range(len(original_prices)):
        if original_prices[i] != None:
            if original_prices[i] > maxPrice:
                maxPrice = original_prices[i]

    #number of none count in originalPrices
    noneCount = 0

    #check only past 'num_update' updates of a stock's values
    if len(original_prices) > num_updates_for_variance:
        # for i in range(num_updates_for_variance - 1, 0, -1):
        for i in range(len(original_prices) - 1, len(original_prices) - 16, -1):
            if original_prices[i] != None:
                insertingPricePercent = original_prices[i] / maxPrice * 100
                new_array_prices.append(insertingPricePercent)
            else:
                noneCount += 1

    #if not enough updates are available, just use the as much updates as possible
    else:
        for i in range(len(original_prices) - 1, -1, -1):
            if original_prices[i] != None:
                new_array_prices.append(original_prices[i] / maxPrice * 100) 
            else:
                noneCount += 1

    #check only past 'num_update' updates of a stock's 'returns on investment'
    insertingReturn = 0
    if len(old_Ys) > num_updates_for_variance:
        for i in range(len(old_Ys) - 1, len(old_Ys) - 16, -1):
            if old_Ys[i] != None:
                if old_Ys[i] == 0:
                    insertingReturn = 0
                elif old_Ys[i] == range(len(old_Ys)):
                    insertingReturn = 0
                else:
                    if old_Ys[i-1] != None:
                        insertingReturn = (float(old_Ys[i]) / float(old_Ys[i - 1]) - 1) * 100
                new_array_returns.append(insertingReturn)

    #if not enough updates are available, just use the as much updates as possible
    else:
        for i in range(len(old_Ys) - 1, -1, -1):
            if old_Ys[i] != None:
                if old_Ys[i] == 0:
                    insertingReturn = 0
                elif old_Ys[i] == range(len(old_Ys)):
                    insertingReturn = 0
                else:
                    if old_Ys[i-1] != None:
                        insertingReturn = (float(old_Ys[i]) / float(old_Ys[i - 1]) - 1) * 100
                new_array_returns.append(insertingReturn)

    #find the variance using var function
    # variance = np.var(np.array(new_array_returns).astype(np.float), axis = 0)

    #standard deviation of 'return of investmenet'
    sd_return = np.std(np.array(new_array_returns).astype(np.float), axis = 0)

    #standard deviation of 'prices'
    sd_prices = np.std(np.array(new_array_prices).astype(np.float), axis = 0)

    #actual weighted returning measurement
    returningMeasure = 0.8 * sd_prices + 0.2 * sd_return

    #count the number of changes in the prices
    changes = 0
    statics = 0
    outliers = 0

    #punish slow changing stocks with lowered variance
    for i in range(len(new_array_prices)-1):
        if np.fabs(new_array_prices[i]) < 0.003 or np.fabs(new_array_prices[i+1]) < 0.003 :
            statics += 1
        elif (np.fabs(new_array_prices[i] / new_array_prices[i+1] - 1) > 0.003 ) or (np.fabs(new_array_prices[i+1] / new_array_prices[i] - 1) > 0.003):
            if (np.fabs(new_array_prices[i] / new_array_prices[i+1] - 1) > 0.11 ) or (np.fabs(new_array_prices[i+1] / new_array_prices[i] - 1) > 0.11):
                outliers += 1
            changes += 1
        else:
            statics += 1

    # returningMeasure = returningMeasure * math.pow((1/(outliers+1)), 1/1.5)
    #statics cant be 0
    if statics == 0:
        statics = 1

    #find the ratio between number of changes over number of stable, over the past 15 updates
    changeStaticRatio = changes / statics

    #the more changes, we scale it up more; the more static, we punish it
    #scale up if there is more changes 
    if (changes - 4) > statics :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio
    elif (changes - 3) > statics :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio
    elif (changes - 2) > statics :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio
    #scale down if they are already very close
    elif (changes - 1) > statics :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio
    elif (changes - 1)  == statics :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio
    #scale down if there is more statics
    elif changes < (statics - 8) :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio
    elif changes < (statics - 7) :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio
    elif changes < (statics - 6) :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio
    elif changes < (statics - 5) :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio
    elif changes < (statics - 4) :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio
    elif changes < (statics - 3) :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio

    #still allow scaling up if the differences between statics and changes are not much
    elif changes < (statics - 2) :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio
    elif changes <= (statics - 1) :
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio
    else:
        front = (0.5 * math.pow(returningMeasure, (1/1.4771)))
        middle =  0.5 * math.pow(changeStaticRatio * 100, (1/3.1761))
        end = math.pow((15 - noneCount) / 15, 1)
        normalisationRatio = 1.5
        outlierRatio = math.pow((1/(outliers+1)), 1/1.5)
        returningMeasure = (front + middle) * end * normalisationRatio * outlierRatio

    return returningMeasure

# Word arrays for use in description
low_variance = ['Low', 'Small', 'Stable', 'Quiet', 'Minor']
medium_variance = ['Some', 'Moderate', ' Mild', 'Reasonable']
high_variance = ['High', 'Volatile', 'Unstable', 'Jittery']
extreme_variance = ['Extremely high', 'Very high', 'Very volatile', 'Tumultuous']

extreme_neg_trend = ['extremely downward', 'rapidly dropping', 'plummeting']
high_neg_trend = ['high decreasing', 'strongly downward', 'very negative']
moderate_neg_trend = ['moderate decreasing', 'dropping', 'downward', 'decreasing']
low_neg_trend = ['minor downward', 'slightly downward', 'small decreasing', 'slightly negative']
stable_trend = ['stable', 'constant', 'unchanging', 'consistent']
low_pos_trend = ['minor upward', 'slightly upwards', 'small increasing', 'slightly positive']
moderate_pos_trend = ['moderate increasing', 'climbing', 'upward', 'increasing']
high_pos_trend = ['high increasing', 'strongly upward', 'very positive']
extreme_pos_trend = ['extremely upward', 'rapidly rising', 'skyrocketing']

low_suggestion = ['Low', 'Small', 'Minor']
moderate_suggestion = ['Mild', 'Moderate', 'Some', 'Reasonable']
high_suggestion = ['High', 'Solid', 'Confident', 'Strong']
certain_suggestion = ['Almost certain', 'Very confident', 'Very strong', 'Very high']

connector_options = ['with a', 'and a', 'coupled with a', 'alongside a', 'paired with a']
trend_adjective = ['predicted', 'expected', 'theorised']

# Pray to RNGesus and pick a random option
def rngesus(options): 
    index = randint(0, len(options) - 1)
    return options[index]

# Get sentence to describe situation 
def getSummary(variance, trend, confidence, action):

    # Same
    trend *= 10

    # Initialise
    variance_desc = ""
    connector = rngesus(connector_options)
    trend_desc = ""
    trend_adj = rngesus(trend_adjective)
    suggestion_desc = ""
    action = "buy" if action == 'B' else "sell"

    # Pick variance description
    if variance > 0.1:
        variance_desc = rngesus(extreme_variance)
    elif variance > 0.07:
        variance_desc = rngesus(high_variance)
    elif variance > 0.03:
        variance_desc = rngesus(medium_variance)
    else:
        variance_desc = rngesus(low_variance)

    # Pick trend description 
    if trend > 0.04: 
        trend_desc = rngesus(extreme_pos_trend)
    elif trend > 0.03:
        trend_desc = rngesus(high_pos_trend)
    elif trend > 0.02:
        trend_desc = rngesus(moderate_pos_trend)
    elif trend > 0.01:
        trend_desc = rngesus(low_pos_trend)
    elif trend < -0.04:
        trend_desc = rngesus(extreme_neg_trend)
    elif trend < -0.03:
        trend_desc = rngesus(high_neg_trend)
    elif trend < -0.02:
        trend_desc = rngesus(moderate_neg_trend)
    elif trend < -0.01:
        trend_desc = rngesus(low_neg_trend)
    else: 
        trend_desc = rngesus(stable_trend)

    # Pick confidence description 
    if confidence > 0.95:
        suggestion_desc = rngesus(certain_suggestion)
    elif confidence > 0.85:
        suggestion_desc = rngesus(high_suggestion)
    elif confidence > 0.7:
        suggestion_desc = rngesus(moderate_suggestion)
    else:
        suggestion_desc = rngesus(low_suggestion)

    # Construct full sentence and return
    sentence = variance_desc + " variance " + connector + " " + trend_desc + " " + trend_adj + " trend. " + suggestion_desc + " suggestion to " + action + "."
    return sentence

