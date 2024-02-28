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

    const handleSave = async () => {
        if (!modelerInstance.current) {
            console.error('Modeler is not initialized');
            return;
        }

        await modelerInstance.current.saveXML().then(
            async (xml) => {
                console.log('Saving diagram:', xml)
                try {
                    await axios.put(`${process.env.REACT_APP_BACKEND_URL}/diagrams/${diagramId}`, xml);
                } catch (error) {
                    console.error('Failed to save diagram:', error);
                }
            }
        );
    };


    return (
        <div style={{height: '100vh', width: '100%'}}>
            <div style={{margin: '10px'}}>
                <button onClick={handleSave}>Save Diagram</button>
            </div>
            <div ref={modelerRef} style={{height: '100%', width: '100%'}}></div>
        </div>
    );
};

export default DiagramEditor;
