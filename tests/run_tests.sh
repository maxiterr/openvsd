#/bin/bash

SCRIPT_PATH=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)

echo "Try to start mock server"
nohup python $SCRIPT_PATH/vsd_mock.py 1>$SCRIPT_PATH/mock_access.log 2>&1 &
MOCK_PID=$!
sleep 2

if [ $(kill -0 $MOCK_PID 2>/dev/null; echo $?) -ne 0 ]; then
  echo "Unable to start mock server."
  exit 1
else
  echo "Start server => OK"
fi

echo ""
echo "Launch bats"
bats $SCRIPT_PATH/test.bats
BATS_STATUS=$?

echo ""
echo "Stop mock server"
kill $MOCK_PID
exit $BATS_STATUS
