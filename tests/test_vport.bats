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


@test "Trunk: reset mock" {
    command vsd free-api reset
    command vsd free-api enterprises/92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e/domains --verb POST \
                         --key-value name:Domain \
                         --key-value parentID:92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    command vsd free-api enterprises/92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e/subnets --verb POST --key-value name:Subnet
    command vsd free-api enterprises/92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e/l2domains --verb POST \
                         --key-value name:L2Domain \
                         --key-value parentID:92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    command vsd free-api subnets/255d9673-7281-43c4-be57-fdec677f6e07/vports --verb POST \
                         --key-value parentType:subnet \
                         --key-value domainID:255d9673-7281-43c4-be57-fdec677f6e07 \
                         --key-value name:Vport-1 \
                         --key-value active:True \
                         --key-value type:VM \
                         --key-value trunkRole:SUB_PORT
    command vsd free-api vports/255d9673-7281-43c4-be57-fdec677f6e07 --verb PUT --key-value ID:d1462209-d658-4aaf-bafe-3d359d9b69f4
    command vsd free-api l2domains/255d9673-7281-43c4-be57-fdec677f6e07/vports --verb POST \
                         --key-value parentType:l2domain \
                         --key-value parentID:255d9673-7281-43c4-be57-fdec677f6e07 \
                         --key-value name:Vport-2 \
                         --key-value active:True \
                         --key-value type:VM \
                         --key-value trunkRole:PARENT_PORT
}


@test "Trunk: create with missing element" {
    run vsd trunk-create --vport-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"<name>\"."

    run vsd trunk-create Trunk-1
    assert_fail
    assert_output_contains "Error: Missing option \"--vport-id\"."
}


@test "Trunk: create with enterprise specified" {
    run vsd trunk-create Trunk-1 --vport-id 255d9673-7281-43c4-be57-fdec677f6e07 --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_success
    assert_output_contains_in_table name Trunk-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Trunk: update" {
    skip "Update command doesn't exist yet"
    run vsd trunk-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value description:MyDescription
    assert_success
    assert_output_contains_in_table description MyDescription
}


@test "Trunk: list for a given enterprise" {
    run vsd trunk-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 Trunk-1
}


@test "Trunk: list for a given vport" {
    run vsd trunk-list --vport-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 Trunk-1
}


@test "Trunk: show" {
    run vsd trunk-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name Trunk-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
    assert_output_contains_in_table associatedVPortID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Trunk: delete with --force" {
    run vsd trunk-delete --force 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success

    run vsd trunk-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals 0 "Error: Cannot find object with ID"
}


@test "Trunk: create with vport connected to subnet (try to discover enterprise id)" {
    run vsd trunk-create Trunk-1 --vport-id d1462209-d658-4aaf-bafe-3d359d9b69f4
    assert_success
    assert_output_contains_in_table name Trunk-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07

    command vsd trunk-delete --force 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Trunk: create with vport connected to l2domain (try to discover enterprise id)" {
    run vsd trunk-create Trunk-1 --vport-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name Trunk-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Trunk: delete must failed with 1 sub-port" {
    run vsd trunk-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
#    assert_line_equals 0 "Error: Cannot find object with ID"

    run vsd trunk-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name Trunk-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Trunk: delete must pass with no sub-port" {
    command vsd free-api vports/d1462209-d658-4aaf-bafe-3d359d9b69f4 --verb DELETE
    run vsd trunk-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success

    run vsd trunk-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
}


@test "Virtual IP: reset mock" {
    command vsd free-api reset
    command vsd free-api enterprises/92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e/domains --verb POST \
                         --key-value name:Domain
    command vsd free-api enterprises/92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e/subnets --verb POST --key-value name:Subnet
    command vsd free-api subnets/255d9673-7281-43c4-be57-fdec677f6e07/vports --verb POST \
                         --key-value parentType:subnet \
                         --key-value domainID:255d9673-7281-43c4-be57-fdec677f6e07 \
                         --key-value name:Vport-1 \
                         --key-value active:True \
                         --key-value type:VM \
                         --key-value trunkRole:SUB_PORT
}


@test "Virtual IP: create with missing element" {
    run vsd virtualip-create --vport-id 255d9673-7281-43c4-be57-fdec677f6e07 
    assert_fail
    assert_output_contains "Error: Missing option \"--virtualip\"."

    run vsd virtualip-create --virtualip 123.123.123.123
    assert_fail
    assert_output_contains "Error: Missing option \"--vport-id\"."
}


@test "Virtual IP: create without MAC" {
    run vsd virtualip-create --vport-id 255d9673-7281-43c4-be57-fdec677f6e07 --virtualip 123.123.123.123
    assert_success
    assert_output_contains_in_table virtualIP 123.123.123.123
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Virtual IP: update" {
    run vsd virtualip-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value MAC:11:22:33:44:55:66
    assert_success
    assert_output_contains_in_table MAC 11:22:33:44:55:66

    # Make this virtual valid because mock doesn't create those values
    vsd virtualip-update 255d9673-7281-43c4-be57-fdec677f6e07 \
        --key-value parentType:vport \
        --key-value parentID:255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Virtual IP: list for a given vport" {
    run vsd virtualip-list --vport-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 123.123.123.123
}


@test "Virtual IP: show" {
    run vsd virtualip-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table MAC 11:22:33:44:55:66
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
    assert_output_contains_in_table parentID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Virtual IP: delete" {
    run vsd virtualip-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success

    run vsd virtualip-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals 0 "Error: Cannot find object with ID"
}


@test "Virtual IP: create sould failled with MAC and same-as-vm option" {
    run vsd virtualip-create --vport-id 255d9673-7281-43c4-be57-fdec677f6e07 --virtualip 123.123.123.123 --mac 11:22:33:44:55:66 --mac-from-vm
    assert_fail
    assert_output_contains "Error: When you activate mac-from-vm, do not use the mac option"
}


@test "Virtual IP: create with mac" {
    run vsd virtualip-create --vport-id 255d9673-7281-43c4-be57-fdec677f6e07 --virtualip 123.123.123.123 --mac 11:22:33:44:55:66
    assert_success
    assert_output_contains_in_table MAC 11:22:33:44:55:66
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07

    command vsd virtualip-delete 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Virtual IP: create and try to get mac from vm interface" {
    command vsd free-api vports/255d9673-7281-43c4-be57-fdec677f6e07/vminterfaces --verb POST --key-value name:eth0

    run vsd virtualip-create --vport-id 255d9673-7281-43c4-be57-fdec677f6e07 --virtualip 123.123.123.123 --mac-from-vm
    assert_success
    assert_output_not_contains_in_table MAC

    command vsd virtualip-delete 255d9673-7281-43c4-be57-fdec677f6e07
    command vsd free-api vminterfaces/255d9673-7281-43c4-be57-fdec677f6e07 --verb PUT --key-value MAC:66:77:88:99:aa:bb

    run vsd virtualip-create --vport-id 255d9673-7281-43c4-be57-fdec677f6e07 --virtualip 123.123.123.123 --mac-from-vm
    assert_success
    assert_output_contains MAC 66:77:88:99:aa:bb
}
