import ContextPadProvider from "bpmn-js/lib/features/context-pad/ContextPadProvider";

export default class CustomContextPadProvider extends ContextPadProvider {

    getContextPadEntries(element) {
        var result = super.getContextPadEntries(element);
        // delete result["append.text-annotation"];
        delete result["append.intermediate-event"];
        return result;
    }
}