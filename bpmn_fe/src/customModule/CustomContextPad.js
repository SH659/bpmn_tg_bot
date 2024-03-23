export default class CustomContextPad {
    constructor(bpmnFactory, config, contextPad, create, elementFactory, injector, translate) {
        this.bpmnFactory = bpmnFactory;
        this.create = create;
        this.elementFactory = elementFactory;
        this.translate = translate;

        if (config.autoPlace !== false) {
            this.autoPlace = injector.get('autoPlace', false);
        }

        contextPad.registerProvider(this);
    }

    getContextPadEntries(element) {
        const {
            autoPlace,
            bpmnFactory,
            create,
            elementFactory,
            translate
        } = this;

        function appendServiceTask(suitabilityScore) {
            return function (event, element) {
                if (autoPlace) {
                    const businessObject = bpmnFactory.create('bpmn:Task');

                    businessObject.suitable = suitabilityScore;

                    const shape = elementFactory.createShape({
                        type: 'bpmn:Task',
                        businessObject: businessObject
                    });

                    autoPlace.append(element, shape);
                } else {
                    appendServiceTaskStart(event, element);
                }
            };
        }

        function appendServiceTaskStart(suitabilityScore) {
            return function (event) {
                const businessObject = bpmnFactory.create('bpmn:Task');

                businessObject.suitable = suitabilityScore;

                const shape = elementFactory.createShape({
                    type: 'bpmn:Task',
                    businessObject: businessObject
                });

                create.start(event, shape, element);
            };
        }

        return {};
    }
}


CustomContextPad.$inject = [
    'bpmnFactory',
    'config',
    'contextPad',
    'create',
    'elementFactory',
    'injector',
    'translate'
];