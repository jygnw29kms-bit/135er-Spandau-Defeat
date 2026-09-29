<?php

$EM_CONF[$_EXTKEY] = [
    'title' => '135er - Spandau Strike Sitepackage',
    'description' => 'TYPO3 v12/v13 sitepackage for the Spandau Strike clan and community website.',
    'category' => 'templates',
    'author' => '135er Spandau Strike',
    'author_email' => '',
    'state' => 'stable',
    'clearCacheOnLoad' => true,
    'version' => '1.0.0',
    'constraints' => [
        'depends' => [
            'typo3' => '12.4.0-13.4.99',
            'fluid_styled_content' => '12.4.0-13.4.99',
            'felogin' => '12.4.0-13.4.99',
        ],
        'conflicts' => [],
        'suggests' => [
            'femanager' => '8.0.0-8.99.99',
        ],
    ],
];
