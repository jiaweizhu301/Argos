PID=$(cat redirect_pid 2>/dev/null)
sudo kill $PID > /dev/null 2>&1
