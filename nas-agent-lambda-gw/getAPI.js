module.exports.apikeys = (serverless) => {

    const stage = process.env.nas_stage;
    let name = 'cco-lmsgw-' + stage + '--key';
    const retVal = {};

    if (process.env.nas_keyname) {
        name = process.env.nas_keyname;
    }

    if (process.env.nas_keyvalue) {
        // the variable is defined
        const value = process.env.nas_keyvalue;
        retVal[stage] = [{
            name: name,
            value: value
        }];
    }
    else {
        retVal[stage] = [{
            name: name
        }];
    }

    serverless.cli.consoleLog(retVal);
    return retVal;
}