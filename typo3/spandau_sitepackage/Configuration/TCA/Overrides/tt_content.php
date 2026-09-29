<?php

declare(strict_types=1);

use TYPO3\CMS\Core\Utility\ExtensionManagementUtility;

defined('TYPO3') or die();

(static function (): void {
    $contentType = 'spandau_player_card';

    ExtensionManagementUtility::addTCAcolumns('tt_content', [
        'tx_spandau_kd' => [
            'exclude' => true,
            'label' => 'K/D – Abschüsse pro Tod',
            'description' => 'K/D-Ratio des Spielers, zum Beispiel 1,42.',
            'config' => [
                'type' => 'input',
                'size' => 10,
                'default' => '0.00',
                'eval' => 'trim,double2',
            ],
        ],
        'tx_spandau_winrate' => [
            'exclude' => true,
            'label' => 'Siegesquote in Prozent',
            'description' => 'Ganzzahliger Wert zwischen 0 und 100.',
            'config' => [
                'type' => 'input',
                'size' => 10,
                'default' => 0,
                'eval' => 'trim,int',
                'range' => [
                    'lower' => 0,
                    'upper' => 100,
                ],
            ],
        ],
    ]);

    ExtensionManagementUtility::addTcaSelectItem(
        'tt_content',
        'CType',
        [
            'label' => '135er – Spielerkarte',
            'value' => $contentType,
            'group' => 'default',
            'description' => 'Spielerprofil mit Kiez-Rolle, Bio, FAL-Bild, K/D und Siegesquote.',
        ],
        'textmedia',
        'after'
    );

    $GLOBALS['TCA']['tt_content']['ctrl']['typeicon_classes'][$contentType] = 'content-card';

    $GLOBALS['TCA']['tt_content']['types'][$contentType] = [
        'showitem' => '
            --div--;Kiez-Profil,
                --palette--;;headers,
                subheader,
                bodytext,
                image,
            --div--;Kiez-Statistik,
                tx_spandau_kd,
                tx_spandau_winrate,
            --div--;LLL:EXT:core/Resources/Private/Language/Form/locallang_tabs.xlf:access,
                --palette--;;hidden,
                --palette--;;access,
            --div--;LLL:EXT:core/Resources/Private/Language/Form/locallang_tabs.xlf:categories,
                categories,
            --div--;LLL:EXT:core/Resources/Private/Language/Form/locallang_tabs.xlf:extended,
        ',
        'columnsOverrides' => [
            'header' => [
                'label' => 'Ingame-Name',
            ],
            'subheader' => [
                'label' => 'Rolle im Kiez',
                'description' => 'Zum Beispiel IGL, AWPer, Entry Fragger oder Support.',
            ],
            'bodytext' => [
                'label' => 'Dit is der Spieler',
                'description' => 'Kurze Bio im Berliner Kiez-Ton.',
                'config' => [
                    'enableRichtext' => true,
                ],
            ],
            'image' => [
                'label' => 'Spieler- oder Kiez-Foto',
            ],
        ],
    ];
})();
