#/bin/bash

# Copyright 2015 Maxime Terras <maxime.terras@numergy.com>
# Copyright 2015 Pierre Padrixe <pierre.padrixe@gmail.com>
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


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

exit_script() {
  echo ""
  echo "Stop mock server"
  kill $MOCK_PID
  exit $BATS_STATUS
}

TEST_LIST="
vsdcli
enterprise
license
domain
subnet
user
dhcp"

for test in $TEST_LIST; do
  echo ""
  echo "Run bats for $test"
  cd $SCRIPT_PATH
  bats $SCRIPT_PATH/test_${test}.bats
  BATS_STATUS=$?
  if [ $BATS_STATUS -ne 0 ]; then
    echo ""
    echo "#############################"
    echo "#     Test failled !        #"
    echo "#############################"
    exit_script
  fi
done

echo ""
echo "#############################"
echo "# All tests pass correctly  #"
echo "#############################"

BATS_STATUS=0
exit_script
