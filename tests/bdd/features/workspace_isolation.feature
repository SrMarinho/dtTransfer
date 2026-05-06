Feature: Workspace isolation
  As an engine operator
  I want entities of different workspaces fully isolated
  So that one workspace cannot accidentally read or write another's data

  Scenario: Two YAML workspaces register entities under their own namespace
    Given a clean registry
    And a YAML workspace "alpha" with entity "foo"
    And a YAML workspace "beta" with entity "bar"
    When both workspaces register their entities
    Then table "alpha/foo" exists in EntityRegistry
    And table "beta/bar" exists in EntityRegistry
    And table "alpha/bar" does not exist
    And table "beta/foo" does not exist

  Scenario: External workspace dir adds workspaces alongside built-in
    Given a clean registry
    And built-in workspaces are loaded
    And an external workspace dir with "tenantA"
    When the loader runs with both dirs
    Then the registry contains "tenantA"
    And the registry contains "biSenior"
