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


@test "Pep8: vsd_route.py" {
    command pep8 --first ../open_vsdcli/vsd_route.py
}


@test "VSD mock: reset" {
    command vsd free-api reset
    command vsd free-api enterprises/92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e/domains --verb POST --key-value name:Domain
}


@test "Static route: create with missing element" {
    run vsd staticroute-create --address 192.168.0.0 --mask 255.255.255.0 --gateway 10.0.0.1
    assert_fail
    assert_line_contains -1 "Error: You must specify one and only one id in"

    run vsd staticroute-create --domain-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --mask 255.255.255.0 --gateway 10.0.0.1
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--address\"."

    run vsd staticroute-create --domain-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --address 192.168.0.0 --gateway 10.0.0.1
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--mask\"."

    run vsd staticroute-create --domain-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --address 192.168.0.0 --mask 255.255.255.0
    assert_fail
    assert_line_equals -1 "Error: Missing option \"--gateway\"."
}


@test "Static route: create" {
    run vsd staticroute-create --domain-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0 --mask 255.255.255.0 --gateway 10.0.0.1
    assert_success
    assert_output_contains_in_table address 192.168.0.0
    assert_output_contains_in_table netmask 255.255.255.0
    assert_output_contains_in_table nextHopIp 10.0.0.1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}

@test "Static route: create with bfd enable" {
    # Reset mock first
    command vsd free-api reset
    command vsd free-api enterprises/92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e/domains --verb POST --key-value name:Domain

    run vsd staticroute-create --domain-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0 --mask 255.255.255.0 --gateway 10.0.0.1 --bfd-enabled
    assert_success
    assert_output_contains_in_table BFDEnabled True
}


@test "Static route: update" {
    run vsd staticroute-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value nextHopIp:10.1.1.1
    assert_success
    assert_output_contains_in_table nextHopIp 10.1.1.1

    # Make this subnet valid because mock doesn't create those values
    vsd staticroute-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value IPType:IPV4
}


@test "Static route: list for a given domain" {
    run vsd staticroute-list --domain-id 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 192.168.0.0/24
}



@test "Static route: create with show-only" {
    run vsd --show-only ID staticroute-create --domain-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0 --mask 255.255.255.0 --gateway 10.0.0.1
    assert_success
    assert_line_equals 0 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Static route: delete" {
    run vsd staticroute-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success

    run vsd subnet-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_fail

    run vsd staticroute-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
}

@test "Static route: Test mask format" {
    run vsd staticroute-create --domain-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0 --mask 25 --gateway 10.0.0.1
    assert_success
    assert_output_contains_in_table address 192.168.0.0
    assert_output_contains_in_table netmask 255.255.255.128
    assert_output_contains_in_table nextHopIp 10.0.0.1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07

    run vsd staticroute-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success

    run vsd staticroute-create --domain-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0 --mask 14 --gateway 10.0.0.1
    assert_success
    assert_output_contains_in_table address 192.168.0.0
    assert_output_contains_in_table netmask 255.252.0.0
    assert_output_contains_in_table nextHopIp 10.0.0.1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07

    run vsd staticroute-delete 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success

    run vsd staticroute-create --domain-id 255d9673-7281-43c4-be57-fdec677f6e07 --address 192.168.0.0 --mask 5 --gateway 10.0.0.1
    assert_success
    assert_output_contains_in_table address 192.168.0.0
    assert_output_contains_in_table netmask 248.0.0.0
    assert_output_contains_in_table nextHopIp 10.0.0.1
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07
}
