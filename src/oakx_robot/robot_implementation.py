import logging
from abc import ABC
from dataclasses import dataclass
from typing import Any, Iterable, Optional

import oaklib.datamodels.validation_datamodel as vdm
from oaklib.datamodels.vocabulary import DEFAULT_PREFIX_MAP, OBO_PURL
from oaklib.interfaces import ValidatorInterface
from oaklib.interfaces.basic_ontology_interface import PREFIX_MAP
from oaklib.interfaces.rdf_interface import RdfInterface
from oaklib.types import CURIE, URI
from py4j.java_gateway import JavaGateway

OWL_NOTHING = 'owl:Nothing'

# https://robot.obolibrary.org/python
# Not required when running `robot python` from the command line:
# launch_gateway(jarpath='bin/robot.jar',
#               classpath='org.obolibrary.robot.PythonOperation',
#               port=25333,
#               die_on_exit=True)

gateway = JavaGateway()


@dataclass
class RobotImplementation(RdfInterface, ValidatorInterface):
    robot_ontology: Any = None
    robot_gateway: Any = None
    reasoner: Any = None

    def __post_init__(self):
        if self.robot_ontology is None:
            io_helper = gateway.jvm.org.obolibrary.robot.IOHelper()
            path = self.resource.slug
            ontology = io_helper.loadOntology(path)
            self.robot_ontology = ontology
            self.robot_gateway = gateway.jvm.org.obolibrary.robot
            rf = gateway.jvm.org.semanticweb.elk.owlapi.ElkReasonerFactory()
            self.reasoner = rf.createReasoner(ontology)

    def get_prefix_map(self) -> PREFIX_MAP:
        # TODO
        # return {'rdfs': str(RDFS)}
        return DEFAULT_PREFIX_MAP

    # def store(self, resource: OntologyResource) -> None:
    #    SparqlBasicImpl.dump(self.engine, resource)

    def curie_to_uri(self, curie: CURIE, strict: bool = False) -> URI:
        if curie.startswith('http'):
            return curie
        pm = self.get_prefix_map()
        if ':' in curie:
            toks = curie.split(':')
            if len(toks) > 2:
                logging.warning(f'CURIE should not contain double colons: {toks}')
                pfx = toks[0]
                local_id = '_'.join(toks[1:])
            else:
                pfx, local_id = toks
            if pfx in pm:
                return f'{pm[pfx]}{local_id}'
            else:
                return f'http://purl.obolibrary.org/obo/{pfx}_{local_id}'
        else:
            logging.warning(f'Not a curie: {curie}')
            return curie

    def uri_to_curie(self, uri: URI, strict=True) -> Optional[CURIE]:
        # TODO: do not hardcode OBO
        pm = self.get_prefix_map()
        for k, v in pm.items():
            if uri.startswith(v):
                return uri.replace(v, f'{k}:')
        if uri.startswith(OBO_PURL):
            uri = uri.replace(OBO_PURL, "")
            return uri.replace('_', ':')
        return uri

    def all_entity_curies(self) -> Iterable[CURIE]:
        ontology = self.robot_ontology
        entities = self.robot_gateway.OntologyHelper.getEntities(ontology).toArray()
        for e in entities:
            yield self.uri_to_curie(e.getIRI().toString())

    def is_coherent(self) -> bool:
        if len(list(self.unsatisfiable_classes())) > 0:
            return False
        elif not self.reasoner.isConsistent():
            return False
        else:
            return True

    def unsatisfiable_classes(self, exclude_nothing=True) -> Iterable[CURIE]:
        ontology = self.robot_ontology
        reasoner = self.reasoner
        for c in ontology.getClassesInSignature().toArray():
            if not reasoner.isSatisfiable(c):
                curie = self.uri_to_curie(c.getIRI().toString())
                if curie == OWL_NOTHING and exclude_nothing:
                    continue
                yield curie

    def validate(self, configuration: vdm.ValidationConfiguration = None) -> Iterable[vdm.ValidationResult]:
        for c in self.unsatisfiable_classes():
            yield vdm.ValidationResult(subject=c,
                                       type='owl:Nothing',
                                       severity=vdm.SeverityOptions(vdm.SeverityOptions.ERROR))
