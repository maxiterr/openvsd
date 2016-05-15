#!/usr/bin/env bats

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


load helpers
source common.bash


@test "Pep8: vsdcli.py" {
    command pep8 --first ../open_vsdcli/vsdcli.py
}


@test "Pep8: vsd_client.py" {
    command pep8 --first ../open_vsdcli/vsd_client.py
}


@test "Pep8: vsd_common.py" {
    command pep8 --first ../open_vsdcli/vsd_common.py
}


@test "VSD client: is available" {
    command -v vsd
}


@test "VSD client: invoking without command prints usage" {
    run vsd
    assert_success
    assert_line_contains 0 "Usage: vsd [OPTIONS] COMMAND [ARGS]..."
}


@test "VSD client: invoking with wrong command prints usage" {
    run vsd azertyuiop
    assert_fail
    assert_line_contains 0 "Usage: vsd [OPTIONS] COMMAND [ARGS]..." ]
}


@test "VSD client: print creds example" {
    run vsd --creds
    assert_success
    assert_output_contains "export VSD_USERNAME"
    assert_output_contains "export VSD_PASSWORD"
    assert_output_contains "export VSD_ORGANIZATION"
    assert_output_contains "export VSD_URL"
}


@test "VSD client: print version" {
    run vsd --version
    assert_success
    echo "$output" | grep -e "^[0-9]*\.[0-9]*\.[0-9]*$"
}


@test "VSD client: request bag object" {
    run vsd enterprise-show bad-object
    assert_fail
    assert_line_contains 0 "Unknown Error: VSD returns"
}


@test "VSD client: run with debug option" {
    run vsd --debug me-show
    assert_success
    assert_line_contains 1 "# Request"
    assert_line_contains 2 "# Method: "
    assert_line_contains 3 "# URL: "
    assert_line_contains 4 "# Headers:"
    assert_line_contains 5 "#    {"
    assert_line_contains 6 "#        \"X-Nuage-Organization\":"
    assert_line_contains 7 "#        \"Content-Type\":"
    assert_line_contains 8 "#        \"Authorization\":"
    assert_line_contains 9 "#    }"
    assert_line_contains 10 "# Parameters: "
    assert_line_contains 12 "# Response"
    assert_line_contains 13 "# Status code: "
    assert_line_contains 14 "# Headers:"
    assert_line_contains 15 "#    {"
    assert_line_contains 16 "#        \"Date\":"
    assert_line_contains 17 "#        \"Content-Length\":"
    assert_line_contains 18 "#        \"Content-Type\":"
    assert_line_contains 19 "#        \"Server\":"
    assert_line_contains 20 "#    }"
    assert_line_contains 21 "# Body: "
}


@test "VSD client: test authentication and create APIkey file" {
    if [ -f ${APIKey} ]; then
        rm -f ${APIKey}
    fi
    [ ! -f ${APIKey} ]

    run vsd enterprise-list
    assert_success
    [ -f ${APIKey} ]
}


@test "VSD client: second connexion without authentication" {
    [ -f ${APIKey} ]
    run vsd --debug enterprise-list
    assert_success
    assert_output_not_contains "/nuage/api/v1_0/me"
}


@test "VSD client: force authentication" {
    [ -f ${APIKey} ]
    run vsd --debug --force-auth enterprise-list
    assert_success
    assert_output_contains "/nuage/api/v1_0/me"
}


@test "VSD client: make wrong authentication" {
    run vsd --vsd-username bad-user me-show
    assert_fail
    assert_line_contains 0 "Error: Athentication failed. Please verify your credentials."
}


@test "VSD client: convert date to human readable format" {
    run vsd me-show
    assert_success
    assert_output_contains_in_table DateDecodeDate '2016-07-25 12:00:00 UTC'
    assert_output_contains_in_table DateNotDecode 1469448000000
    assert_output_contains_in_table ExpiryDecodeExpiry '2016-07-25 12:00:00 UTC'
}


@test "free-api: use with non-existing verb" {
    run vsd free-api enterprises --verb FALSE
    assert_fail
    assert_line_equals -1 'Error: Invalid value for "--verb": invalid choice: FALSE. (choose from PUT, GET, POST, DELETE)'
}


@test "free-api: list all enterprises (GET as default)" {
    run vsd free-api enterprises
    assert_success
    assert_output_contains '"name": "nulab-1"'
    assert_output_contains '"name": "nulab-2"'
}


@test "free-api: list all enterprises with GET" {
    run vsd free-api enterprises --verb GET
    assert_success
    assert_output_contains '"name": "nulab-1"'
    assert_output_contains '"name": "nulab-2"'
}


@test "free-api: create enterprise with POST and key-value" {
    run vsd free-api enterprises --verb POST --key-value 'name:enterpriseTest'
    assert_success
    assert_line_equals 0 '['
    assert_line_equals 1 '    {'
    assert_line_equals 2 '        "ID": "255d9673-7281-43c4-be57-fdec677f6e07", '
    assert_line_equals 3 '        "description": "None", '
    assert_line_equals 4 '        "name": "enterpriseTest"'
    assert_line_equals 5 '    }'
    assert_line_equals 6 ']'
}


@test "free-api: delete enterprise with DELETE" {
    run vsd free-api enterprises/255d9673-7281-43c4-be57-fdec677f6e07?responseChoice=1 --verb DELETE
    assert_success
    assert_line_equals 0 '{}'
}


@test "free-api: update enterprise with PUT and body" {
    run vsd free-api enterprises/255d9673-7281-43c4-be57-fdec677f6e07 --verb PUT --body '[{ "name": "new-enterprise", "description": "Test" }]'
    assert_success
    assert_line_equals 0 '{}'
}


@test "free-api: body needs to be a valid JSON" {
    run vsd free-api enterprises/255d9673-7281-43c4-be57-fdec677f6e07 --verb PUT --body '[{ "name": }]'
    assert_fail
    assert_line_equals -1 'Error: Body could not be decoded as JSON'
}


@test "free-api: key-value and body are incompatible" {
    run vsd free-api enterprises --body '[{ "name":"test" }]' --key-value 'name:test'
    assert_fail
    assert_line_equals -1 'Error: Use body or key-value'
}
