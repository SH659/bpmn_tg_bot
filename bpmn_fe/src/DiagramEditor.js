import React, {useEffect, useRef, useState} from 'react';
import {useParams} from 'react-router-dom';
import axios from 'axios';
import BpmnModeler from 'bpmn-js/lib/Modeler';

const DiagramEditor = () => {
    const {diagramId} = useParams();
    const modelerRef = useRef(null);
    const [modeler, setModeler] = useState(null);

    useEffect(() => {
        const initializeModeler = () => {
            if (modelerRef.current && !modeler) {
                const newModeler = new BpmnModeler({
                    container: modelerRef.current,
                });
                setModeler(newModeler);
                return newModeler;
            }
            return modeler;
        };

        const fetchAndLoadDiagram = async (bpmnModeler) => {
            try {
                const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/diagrams/${diagramId}`);
                const {xml} = response.data;
                await bpmnModeler.importXML(xml);
            } catch (error) {
                console.error('Failed to fetch or import diagram:', error);
            }
        };

        const bpmnModeler = initializeModeler();
        if (bpmnModeler) {
            fetchAndLoadDiagram(bpmnModeler);
        }
    }, [diagramId, modeler]);

    return (
        <div style={{height: '100vh', width: '100%'}}>
            <div ref={modelerRef} style={{height: '100%', width: '100%'}}></div>
        </div>
    );
};

export default DiagramEditor;
