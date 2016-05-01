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


@test "Pep8: vsd_license.py" {
    command pep8 --first ../open_vsdcli/vsd_license.py
}


@test "License: create" {
    run vsd license-create 12Z1223E23E23E23E23E23OMEX2KEOJ3EPOJ2A3EPXJP34RJC4P5IOJVPOIYJECEOP4XJPRO4JC5SRVDCOTJQXZQJ4PCJT5P
    assert_success
    assert_output_contains company Compagny-1
    assert_output_not_contains license
}


@test "License: show" {
    run vsd license-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains company Compagny-1
    assert_output_not_contains license
}


@test "License: show with verbose" {
    run vsd license-show 255d9673-7281-43c4-be57-fdec677f6e07 --verbose
    assert_success
    assert_output_contains company Compagny-1
    assert_output_not_contains license
    assert_line_contains -1 "License: 12Z1223E23E2"
}


@test "License: list" {
    run vsd license-list
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 Compagny-1
}


@test "License: delete" {
    run vsd license-delete 255d9673-7281-43c4-be57-fdec677f6e07 --yes
    assert_success
    assert_output_empty
    run vsd license-list
    assert_success
    assert_output_not_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 Compagny-1
}

