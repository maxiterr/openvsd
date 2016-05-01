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


@test "Pep8: vsd_subnet.py" {
    command pep8 --first ../open_vsdcli/vsd_subnet.py
}


@test "Subnet: create without missing element" {
    run vsd subnet-create --zone-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0 --netmask 255.255.255.0
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"name\"."

    run vsd subnet-create Subnet-1 --zone-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--netmask\"."

    run vsd subnet-create Subnet-1 --zone-id 255d9673-7281-43c4-be57-fdec677f6e07 --netmask 255.255.255.0
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--address\"."

    run vsd subnet-create Subnet-1 --address 192.168.0.0 --netmask 255.255.255.0
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--zone-id\"."
}


@test "Subnet: create" {
    run vsd subnet-create Subnet-1 --zone-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0 --netmask 255.255.255.0
    assert_success
    assert_output_contains_in_table name Subnet-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: update" {
    run vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value netmask:255.255.255.0 --key-value gateway:192.168.0.1
    assert_success
    assert_output_contains_in_table netmask 255.255.255.0
    assert_output_contains_in_table gateway 192.168.0.1

    # Make this subnet valid because mock doesn't create those values
    vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value routeTarget:65000
    vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value routeDistinguisher:100
    vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value externalID:255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: list for a given zone" {
    run vsd subnet-list --zone-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table Subnet-1 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: list for a given domain" {
    run vsd subnet-list --domain-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table Subnet-1 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: list with filter" {
    run vsd subnet-list --domain-id 255d9673-7281-43c4-be57-fdec677f6e07 --filter Subnet
    assert_success
    assert_output_contains 255d9673-7281-43c4-be57-fdec677f6e07

    run vsd subnet-list --domain-id 255d9673-7281-43c4-be57-fdec677f6e07 --filter noSubnet
    assert_success
    assert_output_not_contains 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: show" {
    run vsd subnet-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name Subnet-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Subnet: delete" {
    run vsd subnet-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success

    run vsd subnet-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals 0 "Error: Cannot find object with ID"
}


@test "Subnet: Create with show-only" {
    run vsd --show-only ID subnet-create Subnet-1 --zone-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0 --netmask 255.255.255.0
    assert_success
    assert_line_equals 0 255d9673-7281-43c4-be57-fdec677f6e07
    # Make this subnet valid because mock doesn't create those values
    vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value routeTarget:65000
    vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value routeDistinguisher:100
    vsd subnet-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value externalID:255d9673-7281-43c4-be57-fdec677f6e07
}
