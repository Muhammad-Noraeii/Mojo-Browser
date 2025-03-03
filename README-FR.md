# Mojo Browser

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-green)](https://pypi.org/project/PyQt5/)
[![GitHub Issues](https://img.shields.io/github/issues/Muhammad-Noraeii/Mojo-Browser)](https://github.com/Muhammad-Noraeii/Mojo-Browser/issues)
[![GitHub Stars](https://img.shields.io/github/stars/Muhammad-Noraeii/Mojo-Browser)](https://github.com/Muhammad-Noraeii/Mojo-Browser/stargazers)

[English Translation](README.md)

[Spanish Translation](README-ES.md)

# Mojo Browser

)

Un navigateur web léger axé sur la confidentialité, construit avec Python et PyQt5. Mojo Browser offre des fonctionnalités de sécurité robustes, la prise en charge des extensions et une interface moderne et personnalisable.

---

## Sommaire

- [Fonctionnalités](#features)
- [Installation](#installation)
- [Utilisation](#usage)
- [Contribution](#contributing)
- [Licence](#license)
- [Remerciements](#acknowledgements)
- [Contact](#contact)

---

## Fonctionnalités

- **Confidentialité & Sécurité** : Blocage des traqueurs, prise en charge des proxys, application du HTTPS et anti-empreinte digitale.
- **Extensions** : Chargez des extensions JavaScript depuis MojoX ou des sources personnalisées.
- **Thèmes** : Options de thèmes Sombre, Clair ou Système.
- **Performance** : Accélération matérielle, suspension des onglets et limites de cache configurables.
- **Moteurs de recherche** : Prend en charge Google, DuckDuckGo, Mojeek, et plus encore.
- **Extras** : Mode lecteur, marque-pages, historique et gestionnaire de téléchargements.

---

## Installation

### Prérequis
- **Python** : 3.8 ou supérieur
- **Dépendances** : PyQt5, PyQtWebEngine, Requests

### Étapes
1. **Clonez le dépôt** :
   ```bash
   git clone https://github.com/Muhammad-Noraeii/Mojo-Browser.git
   cd Mojo-Browser
   ```

2. **Installez les dépendances** :
   ```bash
   pip install PyQt5 PyQtWebEngine requests
   ```
   Alternativement, si un fichier `requirements.txt` est ajouté :
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancez le navigateur** :
   ```bash
   python main.py
   ```

4. **Optionnel** : Ajoutez des icônes dans un dossier `icons/` (par exemple, `app_icon.png`) pour une expérience utilisateur complète.

---

## Utilisation

- Lancez le navigateur avec `python main.py`.
- Utilisez la barre d'outils pour naviguer, gérer les onglets ou accéder aux paramètres.
- Configurez les options de confidentialité, les thèmes et les extensions via le menu Paramètres.
- Double-cliquez sur les marque-pages ou les éléments de l'historique pour visiter les URL enregistrées.

Pour des contrôles plus détaillés, consultez la section [raccourcis](#shortcuts) ci-dessous.

### Raccourcis
- `Ctrl+T` : Nouvel onglet
- `Ctrl+W` : Fermer l'onglet
- `Ctrl+R` ou `F5` : Recharger la page
- `F11` : Basculer en plein écran
- `Ctrl+Shift+R` : Activer/désactiver le mode lecteur

---

## Contribution

Nous accueillons les contributions ! Voici comment commencer :

1. **Forkez le dépôt** : Cliquez sur "Fork" sur GitHub.
2. **Clonez votre Fork** :
   ```bash
   git clone https://github.com/VOTRE_NOM_D_UTILISATEUR/Mojo-Browser.git
   ```
3. **Créez une branche** :
   ```bash
   git checkout -b feature/nom-de-votre-fonctionnalité
   ```
4. **Validez les modifications** :
   ```bash
   git commit -m "Ajoutez votre message ici"
   ```
5. **Poussez vers votre Fork** :
   ```bash
   git push origin feature/nom-de-votre-fonctionnalité
   ```
6. **Soumettez une Pull Request** : Ouvrez une PR sur le dépôt principal.

Veuillez lire nos [Directives de contribution](CONTRIBUTING.md) pour plus de détails.

---

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## Remerciements

- **L'équipe PyQt5** : Pour le puissant framework GUI.
- **Contributeurs** : [Muhammad-Noraeii](https://github.com/Muhammad-Noraeii), [Guguss-31](https://github.com/Guguss-31).
- **Communauté** : Merci à tous les utilisateurs et testeurs !

---

## Contact

- **Mainteneur** : [Muhammad Noraeii](https://github.com/Muhammad-Noraeii)
- **Problèmes** : Signalez les bugs ou suggérez des fonctionnalités [ici](https://github.com/Muhammad-Noraeii/Mojo-Browser/issues).
- **Email** : Muhammad.Noraeii@gmail.com

---

Merci d'utiliser Mojo Browser !

Mettez une étoile au projet si vous l'aimez ! ⭐
