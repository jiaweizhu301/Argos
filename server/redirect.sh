# Kill old process
PID=$(cat redirect_pid 2>/dev/null)
sudo kill $PID > /dev/null 2>&1

# Start new process and store PID
sudo python36 redirect.py >/dev/null 2>&1 &
PID=$!
echo $PID > redirect_pid
