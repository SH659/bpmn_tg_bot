import ReplaceMenuProvider from "bpmn-js/lib/features/popup-menu/ReplaceMenuProvider";
import {isDifferentType} from "bpmn-js/lib/features/popup-menu/util/TypeUtil";
import {is} from "bpmn-js/lib/util/ModelUtil";
import * as replaceOptions from "bpmn-js/lib/features/replace/ReplaceOptions";
import {filter} from "min-dash";

export default class CustomReplaceMenuProvider extends ReplaceMenuProvider {
    getEntries(element) {
        var businessObject = element.businessObject;
        var rules = this._rules;
        var entries;

        if (!rules.allowed('shape.replace', {element: element})) {
            return [];
        }

        var differentType = isDifferentType(element);
        var allowedActions = new Set([
            'replace-with-message-start',
            'replace-with-message-intermediate-throw',
            'replace-with-message-intermediate-catch',
            'replace-with-exclusive-gateway',
            'replace-with-none-end',
            'replace-with-task'
        ])
        var differentTypeAndAllowedAction = (entry) => {
            return differentType && allowedActions.has(entry.actionName)
        }

        // start events
        if (is(businessObject, 'bpmn:StartEvent')) {
            entries = filter(replaceOptions.START_EVENT, differentTypeAndAllowedAction);
            return this._createEntries(element, entries);
        }

        // end events TODO:
        if (is(businessObject, 'bpmn:EndEvent')) {
            entries = filter(replaceOptions.END_EVENT, differentTypeAndAllowedAction);
            return this._createEntries(element, entries);
        }

        // intermediate events
        if (is(businessObject, 'bpmn:IntermediateCatchEvent') ||
            is(businessObject, 'bpmn:IntermediateThrowEvent')) {
            entries = filter(replaceOptions.INTERMEDIATE_EVENT, differentTypeAndAllowedAction);
            return this._createEntries(element, entries);
        }

        // gateways
        if (is(businessObject, 'bpmn:Gateway')) {
            entries = filter(replaceOptions.GATEWAY, differentTypeAndAllowedAction);
            return this._createEntries(element, entries);
        }

        // sequence flows
        if (is(businessObject, 'bpmn:SequenceFlow')) {
            return this._createSequenceFlowEntries(element, replaceOptions.SEQUENCE_FLOW);
        }

        return [];
    }
}