const myHeaders = new Headers();
myHeaders.append("Content-Type", "multipart/form-data; boundary=----WebKitFormBoundary4TDSYb32hopIV3o1");
myHeaders.append("accept", "application/json, text/javascript, */*; q=0.01");
myHeaders.append("accept-encoding", "gzip, deflate, br, zstd");
myHeaders.append("cookie", "_lang=us; _autolang=us; cookies-consent=1721871352; confirmation=Sp67xpXBHZeY226232386sRM; cf_clearance=mKy_IeL4t9gkR.RgTYOfI3jZXlpaSx_0dOUpIcGNjKg-1722676948-1.0.1.1-NTXTjfJEdf.M5J8EmuPlBHdxpIIAfkS1kdzFU.ddpckN8mrWIMGr35wc5HmiFVZxPd.e21zbLVahX.yzUJVu7A; _gid=GA1.2.297228745.1722676948; _gat_gtag_UA_67516667_1=1; __gads=ID=274ad628c2d89cb5:T=1721871346:RT=1722676948:S=ALNI_MY4Ws2UkMN7nX07T9D-9-5sMwXiQg; __gpi=UID=00000ea5712e9c18:T=1721871346:RT=1722676948:S=ALNI_MbmhnCSq0-U4GUQ4xsC4I0Bt3XJug; __eoi=ID=0577e04acefdaa6d:T=1721871346:RT=1722676948:S=AA-AfjbdAs_F3_y6Jht5js18ETY4; cursor=AbMVs7S559R6H7Y6n2y2H7B1OezmoYO6; turnback=logger%2FQdmK4Pc0KwVL%2F; FCNEC=%5B%5B%22AKsRol_asgTImKw66HHUElRj_uJ5J4ipQs4sqtipIO63cBFp-4795pYjOAThVWoH0br_JIfR5EsTFG2XrMQCuE6nSeAOiHB8_TzPjDASMFgkoL_q0Sp33ne6GCOiBKydp34Xoq4y1RXtKFEz6zyvi-2YeC_01xXgvw%3D%3D%22%5D%5D; integrity=86nU2TDrbqB9RTQmp6kv4jhP; _ga_7FSG7D195N=GS1.1.1722676947.10.1.1722676993.14.0.0; _ga=GA1.2.2040753983.1721871345; 37852530250738181=3; _autolang=us; _lang=us; clhf03028ja=14.241.246.5; cursor=AbMVs7S559R6H7Y6n2y2H7B1OezmoYO6");
myHeaders.append("origin", "https://iplogger.org");
myHeaders.append("priority", "u=1, i");
myHeaders.append("referer", "https://iplogger.org/logger/QdmK4Pc0KwVL");
myHeaders.append("sec-ch-ua", "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"");
myHeaders.append("sec-fetch-dest", "empty");
myHeaders.append("sec-fetch-mode", "cors");
myHeaders.append("sec-fetch-site", "same-origin");
myHeaders.append("user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36");
myHeaders.append("x-requested-with", "XMLHttpRequest");

const formdata = new FormData();
formdata.append("interval", "all");
formdata.append("filters", "");
formdata.append("page", "1");
formdata.append("sort", "created");
formdata.append("order", "desc");
formdata.append("code", "QdmK4Pc0KwVL");

const requestOptions = {
  method: "POST",
  headers: myHeaders,
  body: formdata,
  redirect: "follow"
};

fetch("https://iplogger.org/logger/", requestOptions)
  .then((response) => response.text())
  .then((result) => console.log(result))
  .catch((error) => console.error(error));
