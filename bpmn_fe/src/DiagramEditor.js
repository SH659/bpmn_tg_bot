import React, {useEffect, useRef} from 'react';
import {useParams} from 'react-router-dom';
import axios from 'axios';
import BpmnModeler from 'bpmn-js/lib/Modeler';
import customModule from "./customModule";

const DiagramEditor = () => {
    const {diagramId} = useParams();
    const modelerRef = useRef(null);
    const modelerInstance = useRef(null);

    useEffect(() => {
        if (!modelerInstance.current && modelerRef.current) {
            modelerInstance.current = new BpmnModeler({
                container: modelerRef.current,
                additionalModules: [customModule],
            });
        }
    }, [diagramId]);

    useEffect(() => {
        const fetchAndLoadDiagram = async () => {
            try {
                const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/diagrams/${diagramId}`);
                const {xml} = response.data;
                await modelerInstance.current.importXML(xml);
            } catch (error) {
                console.error('Failed to fetch or import diagram:', error);
            }
        };

        if (diagramId) {
            fetchAndLoadDiagram();
        }
    }, [diagramId]);

    return (
        <div style={{height: '100vh', width: '100%'}}>
            <div ref={modelerRef} style={{height: '100%', width: '100%'}}></div>
        </div>
    );
};

export default DiagramEditor;
