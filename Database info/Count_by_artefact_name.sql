SELECT COUNT(*) as 'NUMBER', artifactdb.artefact_types.name as 'IMPLANT TYPE'
FROM artifactdb.image_artefacts
JOIN artifactdb.artefact_types ON artifactdb.artefact_types.id=artifactdb.image_artefacts.artefact_id
WHERE artifactdb.artefact_types.name='Metal Clip'