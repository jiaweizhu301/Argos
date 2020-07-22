# Kill old process
PID=$(cat pid 2>/dev/null)
sudo kill $PID > /dev/null 2>&1

# Start new process and store PID
cd projectargos
sudo python36 app.py server >/dev/null 2>&1 &
PID=$!
echo $PID > ../pid
cd ..
