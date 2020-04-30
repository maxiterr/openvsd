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


@test "Pep8: vsd_vm.py" {
    command pep8 --first ../open_vsdcli/vsd_vm.py
}


@test "VSD mock: reset" {
    command vsd free-api reset
}


@test "Vm: create with missing element" {
    run vsd vm-create --uuid 255d9673-7281-43c4-be57-fdec677f6e07 --vport-id 255d9673-7281-43c4-be57-fdec677f6e07 --mac 11:22:33:44:55:66
    assert_fail
    assert_line_equals -1 "Error: Missing argument \"<name>\"."

    run vsd vm-create Vm-1 --vport-id 255d9673-7281-43c4-be57-fdec677f6e07 --mac 11:22:33:44:55:66
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--uuid\"."

    run vsd vm-create Vm-1 --uuid 255d9673-7281-43c4-be57-fdec677f6e07 --mac 11:22:33:44:55:66
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--vport-id\"."

    run vsd vm-create Vm-1 --uuid 255d9673-7281-43c4-be57-fdec677f6e07 --vport-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--mac\"."
}


@test "Vm: create" {
    run vsd vm-create Vm-1 --uuid 255d9673-7281-43c4-be57-fdec677f6e07 --vport-id 255d9673-7281-43c4-be57-fdec677f6e07 --mac 11:22:33:44:55:66
    assert_success
    assert_output_contains_in_table name Vm-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Vm: update" {
    run vsd vm-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value mac:77:88:99:aa:bb:cc --key-value description:MyDescription
    assert_success
    assert_output_contains_in_table mac 77:88:99:aa:bb:cc
    assert_output_contains_in_table description MyDescription

    # Make this vm valid because mock doesn't create those values
    vsd vm-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value status:RUNNING
    vsd vm-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value hypervisorIP:1.2.3.4
    vsd vm-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value reasonType:RUNNING_UNKNOWN
}


@test "Vm: list for a given enterprise" {
    run vsd vm-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_success
    assert_output_contains_in_table Vm-1 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Vm: list with filter" {
    run vsd vm-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --filter Vm
    assert_success
    assert_output_contains 255d9673-7281-43c4-be57-fdec677f6e07

    run vsd vm-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --filter noVm
    assert_success
    assert_output_not_contains 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Vm: show" {
    run vsd vm-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name Vm-1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
    assert_output_contains_in_table UUID 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Vm: delete" {
    run vsd vm-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success

    run vsd vm-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail
    assert_line_equals 0 "Error: Cannot find object with ID"
}
