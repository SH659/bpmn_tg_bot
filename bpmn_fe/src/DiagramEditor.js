import React, {useEffect, useRef, useState} from 'react';
import {useParams} from 'react-router-dom';
import axios from 'axios';
import BpmnModeler from 'bpmn-js/lib/Modeler';
import customModule from "./customModule";

const DiagramEditor = () => {
    const {diagramId} = useParams();
    const modelerRef = useRef(null);
    const modelerInstance = useRef(null);
    const [diagramName, setDiagramName] = useState('');

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
                const {xml, name} = response.data;
                await modelerInstance.current.importXML(xml);
                setDiagramName(name);
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

        modelerInstance.current.saveXML({format: true}).then(async ({xml}) => {
            console.log('Saving diagram:', xml);
            try {
                await axios.put(`${process.env.REACT_APP_BACKEND_URL}/diagrams/${diagramId}`, {
                    xml,
                    name: diagramName,
                });
            } catch (error) {
                console.error('Failed to save diagram:', error);
            }
        });
    };


    return (
        <div style={{height: '100vh', width: '100%'}}>
            <div style={{margin: '10px'}}>
                <input
                    type="text"
                    value={diagramName}
                    onChange={(e) => setDiagramName(e.target.value)}
                    placeholder="Diagram Name"
                />
                <button onClick={handleSave}>Save Diagram</button>
            </div>
            <div ref={modelerRef} style={{height: '100%', width: '100%'}}></div>
        </div>
    );
};

export default DiagramEditor;
