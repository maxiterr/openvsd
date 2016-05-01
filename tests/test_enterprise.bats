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


@test "Pep8: vsd_enterprise.py" {
    command pep8 --first ../open_vsdcli/vsd_enterprise.py
}


@test "Enterprise: list" {
    run vsd enterprise-list
    assert_success
    assert_output_contains_in_table 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e nulab-1
    assert_output_contains_in_table 5b2cc2f3-2b86-42ec-892d-edde741b2fd4 nulab-2
}


@test "Enterprise: list with filter" {
    run vsd enterprise-list --filter 92a76e6f-2ac4
    assert_success
    assert_output_contains_in_table 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e nulab-1
    assert_output_not_contains_in_table 5b2cc2f3-2b86-42ec-892d-edde741b2fd4 nulab-2
}


@test "Enterprise: show" {
    run vsd enterprise-show 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_success
    assert_output_contains_in_table name nulab-1
    assert_output_contains_in_table ID 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
}


@test "Enterprise: create" {
    run vsd enterprise-create new-enterprise
    assert_success
    assert_output_contains_in_table name new-enterprise
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Enterprise: create existing must fail" {
    run vsd enterprise-create new-enterprise
    assert_fail
    assert_line_contains 0 "Error: Object already exists."
}


@test "Enterprise: delete existing" {
    run vsd enterprise-delete 255d9673-7281-43c4-be57-fdec677f6e07 --yes
    assert_success
    assert_output_empty
}

@test "Enterprise: delete non existing" {
    run vsd enterprise-delete 255d9673-7281-43c4-be57-fdec677f6e07 --yes
    assert_fail
    assert_line_contains 0 "Error: Cannot find object with ID"
}

@test "Enterprise: create with show-only" {
    run vsd --show-only ID enterprise-create new-enterprise
    assert_success
    assert_line_equals 0 "255d9673-7281-43c4-be57-fdec677f6e07"
}


@test "Enterprise: update name" {
    run vsd enterprise-update 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --key-value name:nulab-update
    assert_success
    assert_output_contains name nulab-update
}
