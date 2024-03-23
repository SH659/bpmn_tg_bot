import ContextPadProvider from "bpmn-js/lib/features/context-pad/ContextPadProvider";
import {assign} from "min-dash";

export default class CustomContextPadProvider extends ContextPadProvider {

    getContextPadEntries(element) {
        var translate = this._translate,
            autoPlace = this._autoPlace,
            create = this._create,
            elementFactory = this._elementFactory,
            connect = this._connect,
            modeling = this._modeling,
            popupMenu = this._popupMenu,
            canvas = this._canvas,
            rules = this._rules,
            bpmnFactory = this._bpmnFactory,
            appendPreview = this._appendPreview;

        var result = super.getContextPadEntries(element);
        delete result["append.text-annotation"];
        delete result["append.intermediate-event"];


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

                appendPreview.cleanUp();
            }


            var append = autoPlace ? function (_, element) {
                var shape = elementFactory.createShape(assign({type: type}, options));

                autoPlace.append(element, shape);

                appendPreview.cleanUp();
            } : appendStart;


            var previewAppend = autoPlace ? function (_, element) {

                // mouseover
                appendPreview.create(element, type, options);

                return () => {

                    // mouseout
                    appendPreview.cleanUp();
                };
            } : null;


            return {
                group: 'model',
                className: className,
                title: title,
                action: {
                    dragstart: appendStart,
                    click: append,
                    hover: previewAppend
                }
            };
        }


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
        return result;
    }
}