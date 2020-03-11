-- Function to drop all tables, usefull for when testing populate_db script
-- Order is important due to foriegn keys (reference table need to be deleted after table with FK)
DROP TABLE `artifactdb`.`image_artefacts`;
DROP TABLE `artifactdb`.`images`;
DROP TABLE `artifactdb`.`artefact_types`;
DROP TABLE `artifactdb`.`body_part`;
DROP TABLE `artifactdb`.`laterality`;
DROP TABLE `artifactdb`.`studies`;
DROP TABLE `artifactdb`.`patients`;
DROP TABLE `artifactdb`.`positions`;
