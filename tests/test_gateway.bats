#!/usr/bin/env bats

# Copyright 2015 Maxime Terras <maxime.terras@numergy.com>
# Copyright 2015 Pierre Padrixe <pierre.padrixe@gmail.com>
# Copyright 2016 Eric Jallot <eric.jallot@numergy.com>
#
#    Gatewayd under the Apache Gateway, Version 2.0 (the "Gateway"); you may
#    not use this file except in compliance with the Gateway. You may obtain
#    a copy of the Gateway at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the Gateway is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    Gateway for the specific language governing permissions and limitations
#    under the Gateway.


load helpers
source common.bash


@test "Pep8: vsd_gateway.py" {
    command pep8 --first ../open_vsdcli/vsd_gateway.py
}


@test "VSD mock: reset" {
    command vsd free-api reset
}


@test "Gateway: create" {
    run vsd gateway-create gateway-1 --system-id 1.1.1.1 --personality VRSG
    assert_success
    assert_output_contains_in_table name gateway-1
    assert_output_contains_in_table systemID 1.1.1.1
    assert_output_contains_in_table ID 11111111-1111-1111-111111111111
}


@test "Gateway: create existing must fail" {
   run vsd gateway-create gateway-2 --system-id 1.1.1.1 --personality VRSG
   assert_fail
   assert_line_contains 0 "Error: Object already exists."
}


@test "Gateway: update (description)" {
    run vsd gateway-update 11111111-1111-1111-111111111111 --key-value description:1.1.1.1
    assert_success
    assert_output_contains_in_table description 1.1.1.1
}


@test "Gateway: list" {
    run vsd gateway-list
    assert_success
    assert_output_contains_in_table 11111111-1111-1111-111111111111 1.1.1.1
}


@test "Gateway: list with filter" {
    run vsd gateway-list --filter 11111111
    assert_success
    assert_output_contains_in_table 11111111-1111-1111-111111111111 1.1.1.1
}


@test "Gateway: show" {
    run vsd gateway-show 11111111-1111-1111-111111111111
    assert_success
    assert_output_contains_in_table name gateway-1
}


@test "Gateway: delete" {
    run vsd gateway-delete 11111111-1111-1111-111111111111
    assert_success
    assert_output_empty

    run vsd gateway-show 11111111-1111-1111-111111111111
    assert_fail
    assert_line_equals 0 "Error: Cannot find object with ID"
}
