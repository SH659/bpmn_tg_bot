import React, {useEffect, useRef} from 'react';
import BpmnModeler from 'bpmn-js/lib/Modeler';
import customModule from './custom';
import 'bpmn-js/dist/assets/diagram-js.css'; // Core styles for diagram components
import 'bpmn-js/dist/assets/bpmn-font/css/bpmn.css'; // Icons and fonts

const BPMNModelerComponent = () => {
    const modelerRef = useRef(null); // DOM reference for the container
    const bpmnModeler = useRef(null); // To store the instance of BpmnModeler

    useEffect(() => {
        if (!bpmnModeler.current) {
            bpmnModeler.current = new BpmnModeler({
                container: modelerRef.current,
                additionalModules: [customModule],
                moddleExtensions: {}
            });
        }

        const importDiagram = async () => {
            const response = await fetch('empty.bpmn');
            const diagramXML = await response.text();
            await bpmnModeler.current.importXML(diagramXML)
        };

        importDiagram().catch(err => console.error("Error importing diagram:", err));
    }, []); // Empty dependency array ensures this effect runs once on component mount

    return (
        <div ref={modelerRef} style={{width: '100%', height: '100vh'}}></div>
    );
};

export default BPMNModelerComponent;
