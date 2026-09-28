import { sync } from './lib.mjs'; const { VO } = sync(); console.log('explainer.js written', VO.placeholder ? '(placeholder VO timing)' : '(recorded VO timing)');
