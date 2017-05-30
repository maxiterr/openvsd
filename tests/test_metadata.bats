#!/usr/bin/env bats

# Copyright 2017 Maxime Terras <maxime.terras@sfr.com>
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


@test "Pep8: vsd_metadata.py" {
    command pep8 --first ../open_vsdcli/vsd_metadata.py
}


@test "VSD mock: reset" {
    command vsd free-api reset
}


@test "Metadata tag: create with missing element" {
    run vsd metadatatag-create --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_fail
    assert_output_contains "Error: Missing argument \"name\"."
}


@test "Metadata tag: create for enterprise" {
    run vsd metadatatag-create --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e tagName
    assert_success
    assert_output_contains_in_table name tagName
}


@test "Metadata tag: show" {
    run vsd metadatatag-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table name tagName
}


@test "Metadata tag: update" {
    run vsd metadatatag-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value description:tagDescription
    assert_success
    assert_output_contains_in_table description tagDescription
}

@test "Metadata tag: list" {
    run vsd metadatatag-list --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 tagName
}


@test "Metadata: create" {
    run vsd metadata-create metaExemple --entity enterprise --id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --data "Data exemple"
    assert_success
    assert_output_contains_in_table name metaExemple
}


@test "Metadata: create with one tag" {
    command vsd free-api reset
    run vsd metadata-create metaExemple --entity enterprise --id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --data "Data exemple" --tag 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table metadataTagIDs 255d9673-7281-43c4-be57-fdec677f6e07
}


@test "Metadata: create with multiple tag" {
    command vsd free-api reset
    run vsd metadata-create metaExemple --entity enterprise --id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --data "Data exemple" --tag a5d31e18-1db3-4ec8-8b3d-ef2d8c73b429 --tag f3150550-5a0c-41ec-8811-68fbd3d97dd6
    assert_success
    assert_output_contains_in_table a5d31e18-1db3-4ec8-8b3d-ef2d8c73b429
    assert_output_contains_in_table f3150550-5a0c-41ec-8811-68fbd3d97dd6
}


@test "Metadata: show" {
    command vsd free-api reset
    command vsd metadatatag-create --enterprise-id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e tagName
    command vsd metadata-create metaExemple --entity enterprise --id 92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e --data "Data exemple" --tag 255d9673-7281-43c4-be57-fdec677f6e07
    run vsd metadata-show 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_contains_in_table metadataTagIDs 255d9673-7281-43c4-be57-fdec677f6e07
    assert_output_contains_in_table name metaExemple
    assert_output_contains_in_table ID 255d9673-7281-43c4-be57-fdec677f6e07

    run vsd metadata-show 255d9673-7281-43c4-be57-fdec677f6e07 --list-tag
    assert_success
    assert_output_contains_in_table 255d9673-7281-43c4-be57-fdec677f6e07 tagName

    run vsd metadata-show 255d9673-7281-43c4-be57-fdec677f6e07 --data
    assert_success
    assert_line_equals 0 "Data exemple"
}


@test "Metadata: update" {
    run vsd metadata-update 255d9673-7281-43c4-be57-fdec677f6e07 --key-value name:metaRename
    assert_success
    assert_output_contains_in_table name metaRename
}

@test "Metadata: remove existing tag" {
    run vsd metadata-remove-tag 255d9673-7281-43c4-be57-fdec677f6e07 --tag 255d9673-7281-43c4-be57-fdec677f6e07
    assert_success
    assert_output_not_contains_in_table metadataTagIDs 255d9673-7281-43c4-be57-fdec677f6e07
}

@test "Metadata: remove non existing tag" {
    run vsd metadata-remove-tag 255d9673-7281-43c4-be57-fdec677f6e07 --tag 255d9673-7281-43c4-be57
    assert_fail
    assert_line_equals 0 "Error: There is no tag for metadata 255d9673-7281-43c4-be57-fdec677f6e07"
}

@test "Metadata: add 1st tag" {
    run vsd metadata-add-tag 255d9673-7281-43c4-be57-fdec677f6e07 --tag 4F8FF1EA-E1AB-4590-BBF3-7C302F62F681
    assert_success
    assert_output_contains_in_table metadataTagIDs 4F8FF1EA-E1AB-4590-BBF3-7C302F62F681
}

@test "Metadata: add 2nd tag" {
    run vsd metadata-add-tag 255d9673-7281-43c4-be57-fdec677f6e07 --tag 5FEFC839-47D0-40F6-B35B-05C0A6045C88
    assert_success
    assert_output_contains_in_table 4F8FF1EA-E1AB-4590-BBF3-7C302F62F681
    assert_output_contains_in_table 5FEFC839-47D0-40F6-B35B-05C0A6045C88
}

@test "Metadata: add 2 tag at a time" {
    run vsd metadata-add-tag 255d9673-7281-43c4-be57-fdec677f6e07 --tag 96ACF7F6-D690-4CC9-A6F2-22B018A37D51 --tag A335F5AB-AB63-4C58-9ACA-717A22AC7ACC
    assert_success
    assert_output_contains_in_table 4F8FF1EA-E1AB-4590-BBF3-7C302F62F681
    assert_output_contains_in_table 5FEFC839-47D0-40F6-B35B-05C0A6045C88
    assert_output_contains_in_table 96ACF7F6-D690-4CC9-A6F2-22B018A37D51
    assert_output_contains_in_table A335F5AB-AB63-4C58-9ACA-717A22AC7ACC
}

