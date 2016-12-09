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


@test "Gateway redundant group: create" {
    run vsd gateway-create gateway-1 --system-id 1.1.1.1 --personality VRSG
    assert_success
    assert_output_contains_in_table name gateway-1
    assert_output_contains_in_table systemID 1.1.1.1
    assert_output_contains_in_table ID 11111111-1111-1111-111111111111

    run vsd gateway-create gateway-2 --system-id 2.2.2.2 --personality VRSG
    assert_success
    assert_output_contains_in_table name gateway-2
    assert_output_contains_in_table systemID 2.2.2.2
    assert_output_contains_in_table ID 22222222-2222-2222-222222222222

    run vsd gatewayredundancygroup-create gw-group \
                       --gateway-peer1-id 11111111-1111-1111-111111111111 \
                       --gateway-peer2-id 22222222-2222-2222-222222222222
    assert_success
    assert_output_contains_in_table name gw-group
    assert_output_contains_in_table gatewayPeer1ID 11111111-1111-1111-111111111111
    assert_output_contains_in_table gatewayPeer2ID 22222222-2222-2222-222222222222
    assert_output_contains_in_table redundantGatewayStatus SUCCESS
    assert_output_not_contains_in_table name gw-group-unknown
}


@test "VSD mock: reset" {
    command vsd free-api reset
}


@test "Gateway redundant group: create (with enterprise-id)" {
    run vsd gateway-create gateway-1 --system-id 1.1.1.1 --personality VRSG
    assert_success
    assert_output_contains_in_table name gateway-1
    assert_output_contains_in_table systemID 1.1.1.1
    assert_output_contains_in_table ID 11111111-1111-1111-111111111111

    run vsd gateway-create gateway-2 --system-id 2.2.2.2 --personality VRSG
    assert_success
    assert_output_contains_in_table name gateway-2
    assert_output_contains_in_table systemID 2.2.2.2
    assert_output_contains_in_table ID 22222222-2222-2222-222222222222

    run vsd gatewayredundancygroup-create gw-group --enterprise-id fc3a351e-87dc-46a4-bcf5-8c4bb204bd46 \
                                                   --gateway-peer1-id 11111111-1111-1111-111111111111 \
                                                   --gateway-peer2-id 22222222-2222-2222-222222222222
    assert_success
    assert_output_contains_in_table name gw-group
    assert_output_contains_in_table gatewayPeer1ID 11111111-1111-1111-111111111111
    assert_output_contains_in_table gatewayPeer2ID 22222222-2222-2222-222222222222
    assert_output_contains_in_table redundantGatewayStatus SUCCESS
    assert_output_not_contains_in_table name gw-group-unknown
}


@test "Gateway redundant group: create using member in use must fail" {
   run vsd gatewayredundancygroup-create gw-group2 --enterprise-id fc3a351e-87dc-46a4-bcf5-8c4bb204bd46 \
                                                   --gateway-peer1-id 11111111-1111-1111-111111111111 \
                                                   --gateway-peer2-id 22222222-2222-2222-222222222222
   assert_fail
   assert_line_contains 0 "Error: Gateway x.x.x.x is already part of another Redundancy group"
}


@test "Gateway redundant group: update (description)" {
    run vsd gatewayredundancygroup-update 33333333-3333-3333-333333333333 --key-value description:gateway-group
    assert_success
    assert_output_contains_in_table description gateway-group
}


@test "Gateway redundant group: list" {
    run vsd gatewayredundancygroup-list
    assert_success
    assert_output_contains 1 33333333-3333-3333-333333333333
    assert_output_contains 2 SUCCESS
    assert_output_contains 3 gw-group
}


@test "Gateway redundant group: list with filter" {
    run vsd gatewayredundancygroup-list --filter 333333
    assert_success
    assert_output_contains 1 33333333-3333-3333-333333333333
    assert_output_contains 2 gw-group
    assert_output_contains 3 SUCCESS
}


@test "Gateway redundant group: show" {
    run vsd gatewayredundancygroup-show 33333333-3333-3333-333333333333
    assert_success
    assert_output_contains_in_table name gw-group
    assert_output_contains_in_table redundantGatewayStatus SUCCESS
    assert_output_contains_in_table ID 33333333-3333-3333-333333333333
}


@test "Gateway redundant group: delete" {
    run vsd gatewayredundancygroup-delete 33333333-3333-3333-333333333333
    assert_success
    assert_output_empty

    run vsd gatewayredundancygroup-show 33333333-3333-3333-333333333333
    assert_fail
    assert_line_equals 0 "Error: Cannot find object with ID"
}
