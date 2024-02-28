import PaletteProvider from "bpmn-js/lib/features/palette/PaletteProvider";
import {assign} from "min-dash";

export default class CustomPaletteProvider extends PaletteProvider {
    getPaletteEntries(element) {
        var actions = {},
            create = this._create,
            elementFactory = this._elementFactory,
            spaceTool = this._spaceTool,
            lassoTool = this._lassoTool,
            handTool = this._handTool,
            globalConnect = this._globalConnect,
            translate = this._translate;

        function createAction(type, group, className, title, options) {
            function createListener(event) {
                var shape = elementFactory.createShape(assign({type: type}, options));
                if (options) {
                    shape.businessObject.di.isExpanded = options.isExpanded;
                }
                create.start(event, shape);
            }

            var shortType = type.replace(/^bpmn:/, '');
            return {
                group: group,
                className: className,
                title: title || translate('Create {type}', {type: shortType}),
                action: {
                    dragstart: createListener,
                    click: createListener
                }
            };
        }

        assign(actions, {
            'hand-tool': {
                group: 'tools',
                className: 'bpmn-icon-hand-tool',
                title: translate('Activate the hand tool'),
                action: {
                    click: function (event) {
                        handTool.activateHand(event);
                    }
                }
            },
            'lasso-tool': {
                group: 'tools',
                className: 'bpmn-icon-lasso-tool',
                title: translate('Activate the lasso tool'),
                action: {
                    click: function (event) {
                        lassoTool.activateSelection(event);
                    }
                }
            },
            'space-tool': {
                group: 'tools',
                className: 'bpmn-icon-space-tool',
                title: translate('Activate the create/remove space tool'),
                action: {
                    click: function (event) {
                        spaceTool.activateSelection(event);
                    }
                }
            },
            'global-connect-tool': {
                group: 'tools',
                className: 'bpmn-icon-connection-multi',
                title: translate('Activate the global connect tool'),
                action: {
                    click: function (event) {
                        globalConnect.start(event);
                    }
                }
            },
            'tool-separator': {
                group: 'tools',
                separator: true
            },
            'create.start-event': createAction(
                'bpmn:StartEvent',
                'event',
                'bpmn-icon-start-event-message',
                translate('Create StartEvent'),
                {eventDefinitionType: 'bpmn:MessageEventDefinition'}
            ),
            'create.intermediate-catch-message-event': createAction(
                'bpmn:IntermediateCatchEvent',
                'event',
                'bpmn-icon-intermediate-event-catch-message',
                translate('Create StartEvent'),
                {eventDefinitionType: 'bpmn:MessageEventDefinition'}
            ),
            'create.intermediate-catch-throw-event': createAction(
                'bpmn:IntermediateThrowEvent',
                'event',
                'bpmn-icon-intermediate-event-throw-message',
                translate('Create IntermediateThrowEvent Event'),
                {eventDefinitionType: 'bpmn:MessageEventDefinition'}
            ),
            'create.end-event': createAction(
                'bpmn:EndEvent',
                'event',
                'bpmn-icon-end-event-none',
                translate('Create EndEvent')
            ),
        })

        return actions
    }
}
