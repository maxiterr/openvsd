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


@test "Pep8: vsd_dhcp.py" {
    command pep8 --first ../open_vsdcli/vsd_dhcp.py
}


@test "DHCP option: add with missing element" {
    # Miss subnet-id
    run vsd dhcp-option-add --value 18c0a80ac0a80001 --type 79 --length 08
    assert_fail
    assert_line_contains -1 "Error: You must specify only one id in"

    # Miss value
    run vsd dhcp-option-add --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 --type 79 --length 08
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--value\"."

    # Miss type
    run vsd dhcp-option-add --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 --value 18c0a80ac0a80001 --length 08
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--type\"."

    # Miss length
    run vsd dhcp-option-add --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 --value 18c0a80ac0a80001 --type 79
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--length\"."
}


@test "DHCP option: add" {
    run vsd dhcp-option-add --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 --value 18c0a80ac0a80001 --type 79 --length 08
    assert_success
    assert_output_contains_in_table length 08
    assert_output_contains_in_table value 18c0a80ac0a80001
    assert_output_contains_in_table type 79
}


@test "DHCP option: list for a given subnet" {
    run vsd dhcp-option-list --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table 79 08 18c0a80ac0a80001
}


@test "DHCP option: list with filter" {
    run vsd dhcp-option-list --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 --filter 79
    assert_success
    assert_output_contains_in_table 79 08 18c0a80ac0a80001

    run vsd dhcp-option-list --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 --filter NoValue
    assert_output_not_contains 18c0a80ac0a80001
}


@test "DHCP option: show" {
    UUID=$(vsd dhcp-option-list --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 | grep 18c0a80ac0a80001 | sed 's#| *\([a-f0-9-]*\) |.*#\1#')
    run vsd dhcp-option-show $UUID
    assert_success
    assert_output_contains_in_table length 08
    assert_output_contains_in_table value 18c0a80ac0a80001
    assert_output_contains_in_table type 79
}


@test "DHCP option: delete" {
    UUID=$(vsd dhcp-option-list --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 | grep 18c0a80ac0a80001 | sed 's#| *\([a-f0-9-]*\) |.*#\1#')
    run vsd dhcp-option-delete $UUID
    assert_success

    run vsd dhcp-option-show $UUID
    assert_fail
    assert_line_equals 0 "Error: Cannot find object with ID"
}


@test "DHCP option: create with show-only" {
    run vsd --show-only value dhcp-option-add --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 --value 18c0a80ac0a80001 --type 79 --length 08
    assert_success
    assert_line_equals 0 18c0a80ac0a80001
}


@test "DHCP route: list" {
    run vsd dhcp-route-list --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table 192.168.10.0/24 192.168.0.1 "['79']"
}


@test "DHCP route: add" {
    # If route already exist, add option '79' or 'f9' if necessary
    run vsd dhcp-route-add --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 --subnet 192.168.10.0 --mask 24 --gateway 192.168.0.1
    assert_success
    run vsd dhcp-route-list --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table 192.168.10.0/24 192.168.0.1 "['f9', '79']"
    # Add a second route
    run vsd dhcp-route-add --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 --subnet 192.168.11.0 --mask 24 --gateway 192.168.0.2
    assert_success
    run vsd dhcp-route-list --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table 192.168.10.0/24 192.168.0.1 "['f9', '79']"
    assert_output_contains_in_table 192.168.11.0/24 192.168.0.2 "['f9', '79']"
}


@test "DHCP route: delete" {
    run vsd dhcp-route-delete --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07 --subnet 192.168.10.0 --mask 24 --gateway 192.168.0.1
    assert_success
    run vsd dhcp-route-list --subnet-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_not_contains_in_table 192.168.10.0/24 192.168.0.1
    assert_output_contains_in_table 192.168.11.0/24 192.168.0.2
}
