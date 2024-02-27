import ContextPadProvider from "bpmn-js/lib/features/context-pad/ContextPadProvider";
import {assign} from "min-dash";

export default class CustomContextPadProvider extends ContextPadProvider {

    static $inject = ['config.contextPad', 'injector', 'eventBus', 'contextPad', 'modeling', 'elementFactory', 'connect', 'create', 'popupMenu', 'canvas', 'rules', 'translate'];

    constructor(config, injector, eventBus, contextPad, modeling, elementFactory, connect, create, popupMenu, canvas, rules, translate) {
        super(config, injector, eventBus, contextPad, modeling, elementFactory, connect, create, popupMenu, canvas, rules, translate);
    }

    getContextPadEntries(element) {
        var contextPad = this._contextPad,
            modeling = this._modeling,

            elementFactory = this._elementFactory,
            connect = this._connect,
            create = this._create,
            popupMenu = this._popupMenu,
            canvas = this._canvas,
            rules = this._rules,
            autoPlace = this._autoPlace,
            translate = this._translate;

        var result = super.getContextPadEntries(element);

        function appendAction(type, className, title, options) {

            if (typeof title !== 'string') {
                options = title;
                title = translate('Append {type}', {type: type.replace(/^bpmn:/, '')});
            }

            function appendStart(event, element) {

                var shape = elementFactory.createShape(assign({type: type}, options));
                create.start(event, shape, {
                    source: element
                });
            }


            var append = autoPlace ? function (event, element) {
                var shape = elementFactory.createShape(assign({type: type}, options));

                autoPlace.append(element, shape);
            } : appendStart;


            return {
                group: 'model',
                className: className,
                title: title,
                action: {
                    dragstart: appendStart,
                    click: append
                }
            };
        }

        delete result["append.text-annotation"];
        delete result["append.intermediate-event"];

        if (element.type === "bpmn:Lane" || element.type === "bpmn:Participant") {
            delete result["lane-divide-two"];
            delete result["lane-divide-three"];

            if (element.type === "bpmn:Participant") {
                delete result["connect"];
            }
        }

        if (element.type !== "bpmn:SequenceFlow") {
            assign(result, {
                'append.message-intermediate-event': appendAction(
                    'bpmn:IntermediateCatchEvent',
                    'bpmn-icon-intermediate-event-catch-message',
                    translate('Append MessageIntermediateCatchEvent'),
                    {eventDefinitionType: 'bpmn:MessageEventDefinition'}
                ),
                'append.message-intermediate-throw-event': appendAction(
                    'bpmn:IntermediateThrowEvent',
                    'bpmn-icon-intermediate-event-throw-message',
                    translate('Append Intermediate/Boundary Event'),
                    {eventDefinitionType: 'bpmn:MessageEventDefinition'}
                )
            })
        }

        return result;
    }
}