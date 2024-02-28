import CustomContextPad from './CustomContextPad';
import CustomPalette from './CustomPalette';
import CustomRenderer from './CustomRenderer';
import CustomPaletteProvider from "./CustomPaletteProvider";
import CustomContextPadProvider from "./CustomContextPadProvider";
import CustomReplaceMenuProvider from "./CustomReplaceMenuProvider";

export default {
    __init__: ['customContextPad', 'customPalette', 'customRenderer',
        'paletteProvider',
        'contextPadProvider',
        'replaceMenuProvider'
    ],
    customContextPad: ['type', CustomContextPad],
    customPalette: ['type', CustomPalette],
    customRenderer: ['type', CustomRenderer],
    paletteProvider: ['type', CustomPaletteProvider],
    contextPadProvider: ['type', CustomContextPadProvider],
    replaceMenuProvider: ['type', CustomReplaceMenuProvider]
};
