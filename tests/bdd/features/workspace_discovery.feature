Feature: Workspace discovery
  As an engine operator
  I want workspaces discovered from built-in and external dirs
  So that I can add new workspaces without changing engine code

  Scenario: Discover a built-in YAML workspace
    Given a built-in workspace dir "src/workspaces"
    And a YAML workspace "alpha" exists in built-in
    When the loader discovers workspaces
    Then the registry contains "alpha"
    And workspace "alpha" has kind "yaml"

  Scenario: Discover a built-in Python (legacy) workspace
    Given a built-in workspace dir "src/workspaces"
    And a Python workspace "legacy" exists in built-in
    When the loader discovers workspaces
    Then the registry contains "legacy"
    And workspace "legacy" has kind "python"

  Scenario: Discover external workspace via WORKSPACES_DIR
    Given a built-in workspace dir "src/workspaces"
    And an external workspace dir
    And a YAML workspace "external_one" exists in external
    When the loader discovers workspaces
    Then the registry contains "external_one"

  Scenario: Built-in takes precedence over external on id conflict
    Given a built-in workspace dir "src/workspaces"
    And an external workspace dir
    And a YAML workspace "shared" exists in built-in
    And a YAML workspace "shared" exists in external
    When the loader discovers workspaces
    Then workspace "shared" comes from "built-in"

  Scenario: Invalid workspace folders are ignored
    Given a built-in workspace dir "src/workspaces"
    And an invalid folder "broken" exists in built-in
    When the loader discovers workspaces
    Then the registry does not contain "broken"
