const BASE_URL = "https://demo-qze7.onrender.com";

export async function getClientes() {
  try {
    const response = await fetch(`${BASE_URL}/clientes`);
    if (!response.ok) throw new Error("Error al obtener clientes");
    return await response.json();
  } catch (error) {
    console.error(error);
    return [];
  }
}

export async function createCliente(data) {
  try {
    const response = await fetch(`${BASE_URL}/clientes`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) throw new Error("Error al crear cliente");
    return await response.json();
  } catch (error) {
    console.error(error);
  }
}

export async function getProductos() {
  try {
    const response = await fetch(`${BASE_URL}/productos`);
    if (!response.ok) throw new Error("Error al obtener productos");
    return await response.json();
  } catch (error) {
    console.error(error);
    return [];
  }
}