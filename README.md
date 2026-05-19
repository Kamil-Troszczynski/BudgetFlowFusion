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

The purchase records system is a web application designed for managing and monitoring purchase-related data within a student research club. The frontend was built using Vue.js, the backend is based on FastAPI, and the data is stored in an Oracle Database database. The system allows users to add, edit, and browse purchase records, providing quick access to information and convenient data management.

## Clone repository

```bash
#   With ssh
git clone git@github.com:Kamil-Troszczynski/BudgetFlowFusion.git

#   With https
git clone https://github.com/Kamil-Troszczynski/BudgetFlowFusion.git
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

#   Install npm manager
npm install

#   Run developer mode
npm run dev
```

## How to build frontend in production mode?

```bash
npm run build
```