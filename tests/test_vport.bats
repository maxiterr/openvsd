#!/usr/bin/env bats

# Copyright 2020 Maxime Terras <maxime.terras@numergy.com>
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


@test "Pep8: vsd_vport.py" {
    command pep8 --first ../open_vsdcli/vsd_vport.py
}


@test "VSD mock: reset" {
    command vsd free-api reset
    command vsd free-api enterprises/92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e/subnets --verb POST --key-value name:Subnet
    command vsd free-api enterprises/92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e/l2domains --verb POST --key-value name:L2Domain
}


@test "Vport: create with missing element" {
    run vsd vport-create --type VM --active --address-spoofing ENABLED --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"<name>\"."

    run vsd vport-create Vport-1 --active --address-spoofing ENABLED --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_output_contains "Error: Missing option \"--type\"."

    run vsd vport-create Vport-1 --type VM --active --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_output_contains "Error: Missing option \"--address-spoofing\"."

    run vsd vport-create Vport-1 --type VM --active --address-spoofing ENABLED
    assert_fail
    assert_output_contains "Error: You must specify one and only one id in"

    run vsd vport-create Vport-1 --type VM --active --address-spoofing ENABLED --subnet-id 255 --l2domain-id 255
    assert_fail
    assert_output_contains "Error: You must specify one and only one id in"
}


@test "Vport: create" {
    run vsd vport-create Vport-1 --type VM --active --address-spoofing ENABLED --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name Vport-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
    assert_output_contains_in_table addressSpoofing ENABLED
    assert_output_contains_in_table type VM
    assert_output_contains_in_table active True
}


@test "Vport: update" {
    run vsd vport-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value description:MyDescription
    assert_success
    assert_output_contains_in_table description MyDescription
}


@test "Vport: list for a given subnet" {
    run vsd vport-list --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table Vport-1 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Vport: list for a given l2domain" {
    run vsd vport-list --l2domain-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table Vport-1 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Vport: show" {
    run vsd vport-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name Vport-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
    assert_output_contains_in_table addressSpoofing ENABLED
    assert_output_contains_in_table type VM
    assert_output_contains_in_table active True
}


@test "Vport: delete" {
    run vsd vport-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success

    run vsd vport-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals 0 "Error: Cannot find object with ID"
}

