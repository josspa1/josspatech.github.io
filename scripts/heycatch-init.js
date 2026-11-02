/**
 * HeyCatch client entry for josspatech.com (static multi-page site).
 * Loaded as type=module on every public page that uses site analytics.
 * Follows https://heycatch.ai/agents.md — do not dynamic-import the SDK.
 *
 * Prompt type: web app (no site: 'landing' tag).
 */
import { analytics } from 'https://esm.sh/@heycatch/sdk@0.8.3';

analytics.init({
  projectKey: 'hck_pk_kHHaqwkbOlQRAk0BomIfCNQw-NlPKCCu',
  requestBatching: false,
  install: {
    framework: 'web',
    agent: 'cursor',
  },
});
