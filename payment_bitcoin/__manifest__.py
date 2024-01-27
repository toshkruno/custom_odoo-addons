{
    "name": "Bitcoin Payment Acquirer",
    "category": "Hidden",
    "summary": "Payment Acquirer: Bitcoin Transfer Implementation",
    "version": "15.0.1.0.0",
    "author": "Yagami Light, Odoo Community Association (OCA)",
    "website": "https://toshkruno.github.io/my-portfolio/",
    "license": "LGPL-3",
    "depends": ["payment", "website_sale", "website_sale_payment", "base_automation"],
    "data": [
        "security/ir.model.access.csv",
        "data/base_automation.xml",
        "data/mail_data.xml",
        "data/ir_cron_data.xml",
        "views/bitcoin_views.xml",
        "views/payment_bitcoin_templates.xml",
        "data/payment_acquirer_data.xml",
        "views/counter_qweb.xml",
        "views/cart.xml",
        "views/res_config_settings_view.xml",
        "views/payment_acquirer.xml",
        "views/sale_portal_view.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "payment_bitcoin/static/src/js/bitcoin.js",
            "payment_bitcoin/static/src/js/countdown.js",
            "payment_bitcoin/static/src/css/bitcoin_custom.css",
        ],
    },
    "installable": True,
    "auto_install": False,
}