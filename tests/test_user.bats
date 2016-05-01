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


@test "Pep8: vsd_user.py" {
    command pep8 --first ../open_vsdcli/vsd_user.py
}


@test "User: create with missing element" {
    run vsd user-create --firstname john --lastname doe --email john.doe@nomail.com --password xDz3R --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"username\"."

    run vsd user-create jdoe --firstname john --email john.doe@nomail.com --password xDz3R --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--lastname\"."

    run vsd user-create jdoe --lastname doe --email john.doe@nomail.com --password xDz3R --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--firstname\"."

    run vsd user-create jdoe --lastname doe --firstname john --password xDz3R --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--email\"."

    run vsd user-create jdoe --lastname doe --firstname john --email john.doe@nomail.com --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--password\"."

    run vsd user-create jdoe --lastname doe --firstname john --email john.doe@nomail.com --password xDz3R
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--enterprise-id\"."
}


@test "User: create" {
    run vsd user-create jdoe --firstname john --lastname doe --email john.doe@nomail.com --password xDz3R --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table userName jdoe
    assert_output_contains_in_table email john.doe@nomail.com
    assert_output_contains_in_table firstName john
    assert_output_contains_in_table lastName doe
}


@test "User: show" {
    run vsd user-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table userName jdoe
    assert_output_contains_in_table email john.doe@nomail.com
    assert_output_contains_in_table firstName john
    assert_output_contains_in_table lastName doe
}


@test "User: delete" {
    run vsd user-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_empty
    run vsd user-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_contains 0 "Error: Cannot find object with ID"
}


@test "User: create with --show-only" {
    run vsd --show-only ID user-create jdoe --firstname john --lastname doe --email john.doe@nomail.com --password xDz3R --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_line_equals 0 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Group: create with missing elements" {
    run vsd group-create --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"name\"."

    run vsd group-create group-1
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--enterprise-id\"."
}


@test "Group: create" {
    run vsd group-create group-1 --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07 --description "Test Group"
    assert_success
    assert_output_contains_in_table name group-1
    # ToDo (pierrepadrixe): description not working
    #assert_output_contains_in_table description "Test Group"
}


@test "Group: show" {
    run vsd group-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name group-1
    # ToDo (pierrepadrixe): description not working
    #assert_output_contains_in_table description "Test Group"
}


@test "Group: update" {
    run vsd group-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value "description:Test Group"
    assert_success
    assert_output_contains_in_table description "Test Group"
}


@test "Group: delete" {
    #skip "Group-delete command doesn't exist yet"
    run vsd group-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    run vsd group-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_contains 0 "Error: Cannot find object with ID"
}


@test "Group: create with --show-only" {
    run vsd group-create group-1 --enterprise-id 255d9673-7281-43c4-be57-fdec677f6e07 --description "Test Group"
    assert_success
    assert_output_contains_in_table name group-1
    # ToDo (pierrepadrixe): description not working1
    #assert_output_contains_in_table description "Test Group"
}


@test "Group: add user in group with missing elements" {
    run vsd group-add-user --user-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"group-id\"."

    run vsd group-add-user 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--user-id\"."
}


@test "Group: add user in group" {
    run vsd group-add-user 255d9673-7281-43c4-be57-fdec677f6e07 --user-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_empty
}


@test "Group: delete user in group with missing elements" {
    run vsd group-del-user --user-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"group-id\"."

    run vsd group-del-user 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--user-id\"."
}


@test "Group: delete user in group" {
    run vsd group-del-user 255d9673-7281-43c4-be57-fdec677f6e07 --user-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_empty
}
