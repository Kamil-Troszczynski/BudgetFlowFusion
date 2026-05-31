# BudgetFlowFusion
![](https://img.shields.io/badge/VUE-22.12.0-green?style=plastic
) ![](https://img.shields.io/badge/FastAPI-0.136.1-green?style=plastic
) ![](https://img.shields.io/badge/POSTGRE-SQL-blue?style=plastic
) ![](https://img.shields.io/badge/SQL-Model-purple?style=plastic
) ![](https://img.shields.io/badge/Pydantic-lightgreen?style=plastic
)

Authors:
 - Kamil Troszczyński [Github](https://github.com/Kamil-Troszczynski)
 - Wojciech Fiedoruk [Github](https://github.com/Wojtek901)
 - Miłosz Piecha [Github](https://github.com/Coffee4Cat)
 - Dominik Chmielak [Github](https://github.com/Kamil-Troszczynski)
 - Mateusz Bartosiak [Github](https://github.com/barto159)

The purchase records system is a web application designed for managing and monitoring purchase-related data within a student research club. The frontend was built using Vue.js, the backend is based on FastAPI, the data is created in SQL Model and stored in an PostgreSQL database. The system allows users to add, edit, and browse purchase records, providing quick access to information and convenient data management.

## Current project structure
```bash
BudgetFlowFusion/
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── run.py
│   ├── scripts/
│   │   └── mockup_data.sql
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   ├── relations.py
│   │   └── routes/
│   │       ├── categories_subcategories_routes.py
│   │       ├── fundings_routes.py
│   │       ├── items_routes.py
│   │       ├── lists_routes.py
│   │       ├── login_register_routes.py
│   │       └── shops_routes.py
│   │
│   └── tests/
│       ├── conftest.py
│       └── test_business_logic.py
│
├── frontend/
│   ├── index.html
│   ├── jsconfig.json
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   │
│   ├── public/
│   │   ├── animation.mp4
│   │   ├── favicon.ico
│   │   └── logo.png
│   │
│   └── src/
│       ├── App.vue
│       ├── main.js
│       │
│       ├── components/
│       │   ├── home_page/
│       │   │   └── HomePage.vue
│       │   │
│       │   ├── items_shop_purchase_lists/
│       │   │   ├── AddCategoryModal.vue
│       │   │   ├── AddedItems.vue
│       │   │   ├── AddedShopPurchaseLists.vue
│       │   │   ├── AddItemModal.vue
│       │   │   ├── AddItemToListModal.vue
│       │   │   ├── AddListModal.vue
│       │   │   ├── ShopPurchaseListDetails.vue
│       │   │   └── TreasurerValidation.vue
│       │   │
│       │   ├── login_register_page/
│       │   │   ├── SignIn.vue
│       │   │   └── SignUp.vue
│       │   │
│       │   ├── purchase_request/
│       │   │   └── PurchaseRequest.vue
│       │   │
│       │   ├── settlement/
│       │   │   └── Settlement.vue
│       │   │
│       │   └── ToastNotification.vue
│       │
│       ├── composables/
│       │   ├── useAuth.js
│       │   └── useToast.js
│       │
│       └── router/
│           └── index.js
│
├── docker-compose.yml
└── README.md
```

## Clone repository

```bash
#   With ssh
git clone git@github.com:Kamil-Troszczynski/BudgetFlowFusion.git

#   With https
git clone https://github.com/Kamil-Troszczynski/BudgetFlowFusion.git
```

## Install & prepare Docker

### On Linux Ubuntu
```bash
# Update
 sudo apt-get update

# Install docker
sudo apt install ./docker-desktop-amd64.deb

# Check whether it's work
systemctl --user start docker-desktop

# Close docker menu
 systemctl --user stop docker-desktop
```

### On Windows
[Go to this site and install Docker for Windows OS](https://www.docker.com/get-started/)


## Install Node.js with npm manager

### On Linux Ubuntu
```bash
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash

# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"

# Download and install Node.js:
nvm install 24

# Verify the Node.js version:
node -v
# Should print "v24.15.0".

# Verify npm version:
npm -v
# Should print "11.12.1".
```

### On Windows
```bash
# Download and install Chocolatey:
powershell -c "irm https://community.chocolatey.org/install.ps1|iex"

# Download and install Node.js:
choco install nodejs --version="24.15.0"

# Verify the Node.js version:
node -v
# Should print "v24.15.0".

# Verify npm version:
npm -v
# Should print "11.12.1".
```


## How to launch backend with database?

Launch server and database

```bash
#   Go to directory
cd BudgetFlowFusion

#   Launch infrastructure
docker compose up --build
```

## How to run frontend in dev mode?

```bash
#   Go to frontend directory
cd frontend

#   Install npm manager with packages
npm install

#   Run developer mode
npm run dev
```

## How to build frontend in production mode?

```bash
npm run build
```

## How to look up database?

```bash
docker exec -it budgetflowfusion_db psql -U budgetflowfusion -d budgetflowfusion
```

## How to run tests?

With running container.

```bash
docker exec -it backend python -m pytest tests/
```
