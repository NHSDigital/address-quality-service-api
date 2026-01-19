
// If we don't set this then it will add the "/FHIR/R4/DocumentReference"
context.setVariable("target.copy.pathsuffix", false);
// Write the new path into the variable '/spine-api-gateway/validate'
context.setVariable("target_path", "/spine-api-gateway/validate");

