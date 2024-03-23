import React, {useEffect, useRef, useState} from 'react';
import {useNavigate, useParams} from 'react-router-dom';
import axios from 'axios';
import BpmnModeler from 'bpmn-js/lib/Modeler';
import customModule from "./customModule";
import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap CSS
import '@fortawesome/fontawesome-free/css/all.min.css';
import resizeTask from 'bpmn-js-task-resize/lib';

const DiagramEditor = () => {
    const navigate = useNavigate();
    const {diagramId} = useParams();
    const modelerRef = useRef(null);
    const modelerInstance = useRef(null);
    const [diagramName, setDiagramName] = useState('');
    const [isEditingName, setIsEditingName] = useState(false);

    useEffect(() => {
        if (!modelerInstance.current && modelerRef.current) {
            modelerInstance.current = new BpmnModeler({
                container: modelerRef.current,
                additionalModules: [customModule, resizeTask],
                taskResizingEnabled: true,
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

    const handleNameChange = (e) => {
        if (e.key === 'Enter' || e.type === 'blur') {
            setIsEditingName(false);
            handleSave();
        }
    };

    const handleBack = () => {
        navigate(-1);
    };

    // Function to restart bots by diagram ID
    const restartBotsByDiagramId = async () => {
        try {
            await axios.post(`${process.env.REACT_APP_BACKEND_URL}/bot/tg/restart_by_diagram/${diagramId}`);
        } catch (error) {
            console.error('Failed to restart bots:', error);
            alert('Error restarting bots. Check the console for more details.');
        }
    };

    const assignDefaultBot = async () => {
        try {
            console.log('Assigning default bot', diagramId)
            await axios.put(`${process.env.REACT_APP_BACKEND_URL}/bot/tg/assign_default/${diagramId}`);
        } catch (error) {
            console.error('Failed to assign default bot:', error);
        }
    };


    return (
        <div className="container-fluid" style={{height: '100vh'}}>
            <div className="row mb-3 align-items-center">
                <div className="col-auto">
                    <button className="btn" onClick={handleBack}>
                        <i className="fas fa-arrow-left"></i> Back
                    </button>
                </div>
                <div className="col">
                    <div className="col-12">
                        {isEditingName ? (
                            <input
                                type="text"
                                className="form-control"
                                value={diagramName}
                                onBlur={handleNameChange}
                                onKeyDown={(e) => e.key === 'Enter' && handleNameChange(e)}
                                onChange={(e) => setDiagramName(e.target.value)}
                                autoFocus
                            />
                        ) : (
                            <h3 onClick={() => setIsEditingName(true)} style={{cursor: 'pointer'}}>
                                {diagramName || 'Click to set a diagram name'}
                            </h3>
                        )}
                    </div>
                    <div className="row">
                        <div className="col-12 d-flex align-items-center justify-content-start">
                            <button className="btn btn-primary btn-sm me-2" onClick={handleSave}>Save</button>
                            <button className="btn btn-warning btn-sm me-2" onClick={restartBotsByDiagramId}>
                                Restart Bots
                            </button>
                            <button className="btn btn-success btn-sm me-2" onClick={assignDefaultBot}>
                                Assign Default Bot
                            </button>
                        </div>
                    </div>
                </div>

            </div>
            <hr/>
            <div ref={modelerRef} className="row" style={{
                height: 'calc(100% - 100px)'
            }}></div>
        </div>
    );
};

export default DiagramEditor;
