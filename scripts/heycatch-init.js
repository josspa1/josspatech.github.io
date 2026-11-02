/**
 * HeyCatch client entry for josspatech.com (static marketing / landing site).
 * Loaded as type=module on every public page that uses site analytics.
 * Follows https://heycatch.ai/agents.md — do not dynamic-import the SDK.
 */
import { analytics } from 'https://esm.sh/@heycatch/sdk@0.8.3';

analytics.init({
  projectKey: 'hck_pk_kHHaqwkbOlQRAk0BomIfCNQw-NlPKCCu',
  site: 'landing',
  requestBatching: false,
  install: {
    framework: 'web',
    agent: 'cursor',
  },
});
