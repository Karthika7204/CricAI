export const getFlagUrl = (name: string) => {
  const cleanStr = (s: string) => s?.replace(/['"]/g, '').trim().toLowerCase() || '';
  const n = cleanStr(name);
  const mapping: Record<string, string> = {
    'india': 'in',
    'pakistan': 'pk',
    'sri lanka': 'lk',
    'u.s.a.': 'us',
    'usa': 'us',
    'england': 'gb',
    'australia': 'au',
    'south africa': 'za',
    'new zealand': 'nz',
    'west indies': 'vg',
    'netherlands': 'nl',
    'afghanistan': 'af',
    'scotland': 'gb-sct',
    'bangladesh': 'bd'
  };
  const code = mapping[n] || 'un';
  return `https://flagcdn.com/w40/${code}.png`;
};
