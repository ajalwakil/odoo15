import { registry } from "@web/core/registry";
import { preferencesItem } from "@web/webclient/user_menu/user_menu_items";

export function preferencesItem(env) {
    return {
        type: "item",
        id: "settings",
        description: env._t("Preferences 2"),
        callback: async function () {
            const actionDescription = await env.services.orm.call("res.users", "action_get");
            actionDescription.res_id = env.services.user.userId;
            env.services.action.doAction(actionDescription);
        },
        sequence: 50,
    };
}

registry
    .category("user_menuitems")
    .add("profile", preferencesItem)