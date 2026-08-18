# Circ-Maker

[![CI](https://github.com/Octahedron-apple/Circ-Maker/actions/workflows/ci.yml/badge.svg)](https://github.com/Octahedron-apple/Circ-Maker/actions/workflows/ci.yml) ![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge) ![Logisim](https://img.shields.io/badge/Logisim--Evolution-Compatible-orange?style=for-the-badge)

**Circ-Maker** is a Python-based framework and DSL (Domain Specific Language) designed to programmatically generate fully functional, non-colliding Logisim-Evolution `.circ` files from simple, highly readable code.

> **Built with Test-Driven Development (TDD) 🚀**
> This framework is engineered around rigorous TDD principles. A comprehensive suite of automated Logisim truth-table compilation tests guarantees that the generated routing logic is robust. Automated CI tests continuously validate the underlying channel router against complex short-circuits, ensuring that the circuit logic designed in the DSL is strictly what is produced in the final `.circ` file. 

## Documentation

For a comprehensive guide on how to write circuit definitions using our DSL, as well as setup and generation instructions, please refer to our **[Usage and Syntax Guide](USAGE.md)**.