def get_region(definitions, specifiers):
    identifiers = definitions.get('identifier')
    if identifiers:
        region_identifiers = [identifier['specifier'] for identifier in identifiers if identifier.get('location')]
        for region_identifier in region_identifiers:
            if region_identifier in specifiers:
                specifier = specifiers[region_identifier]
                definition = next(definition for definition in definitions[region_identifier]
                                  if definition['specifier'] == specifier)
                return definition
